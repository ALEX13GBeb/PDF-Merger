from flask import Flask, request, redirect, url_for, send_from_directory, render_template, session
import os
import csv
from werkzeug.utils import secure_filename
from merge import merger_pdf

app = Flask(__name__)
app.secret_key = "my_session_key"

app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MERGED_FOLDER"] = "merged"
app.config["ALLOWED_EXTENSIONS"] = {"pdf"}

# Ensure upload and merged folders exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["MERGED_FOLDER"], exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

@app.route("/")
def index():
    logged_in=session.get("logged_in", False)
    return render_template("index.html", logged_in=logged_in)

@app.route("/signout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("index"))

@app.route("/profile", methods=["GET", "POST"])
def profile_page():
    return render_template("profile.html")

@app.route("/login", methods=["GET", "POST"])
def login_page():

    if request.method == "POST":
        try_login = [request.form.get("login_un"), request.form.get("login_password")]

        login_file_path = "login_data.csv"

        if os.path.isfile(login_file_path):
            with open(login_file_path, "r", newline="", encoding="utf-8") as Llogin_file:
                login_rows = csv.reader(Llogin_file)
                next(login_rows)  # Skip the header row if there is one

                for row in login_rows:
                    available_login = [row[0], row[1]]
                    if try_login == available_login:
                        session.pop("error", None)# Clear any existing error messages
                        ########################
                        session["logged_in"]=True
                        ########################

                        return redirect(url_for("index"))  # Redirect to the index or another page

        # Set an error message in session if login fails
        session["error"] = "Invalid username or password"
        return redirect(url_for("login_page"))  # Redirect to the login page to display the error

    # For GET requests, or if login fails, render the login page
    return render_template("login.html", error=session.pop("error", None))

@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if request.method == "POST":
        # Collect user data from the form
        user_data = {
            "first_name": request.form.get("signup_fn"),
            "last_name": request.form.get("signup_ln"),
            "username": request.form.get("signup_un"),
            "email": request.form.get("signup_email"),
            "password": request.form.get("signup_password"),
        }

        login_data = {
            "username": request.form.get("signup_un"),
            "password": request.form.get("signup_password")
        }

        # Define the path to the CSV file
        Aadmin_file_path = "admin.csv"
        Alogin_file_path = "login_data.csv"

        # Write user_data to CSV file
        admin_exists = os.path.isfile(Aadmin_file_path)
        with open(Aadmin_file_path, mode="a", newline="", encoding="utf-8") as admin_file:
            # newline - ensures blank lines are handled consistently between platforms
            admin_writer = csv.DictWriter(admin_file, fieldnames=user_data.keys())
            # Write header if file is empty
            if not admin_exists:
                admin_writer.writeheader()
            # Write user data
            admin_writer.writerow(user_data)
            print(f"User data written to {Aadmin_file_path}: {user_data}")  # Debugging statement

            login_exists = os.path.isfile(Alogin_file_path)
            with open(Alogin_file_path, "a", newline="", encoding="utf-8") as login_file:
                login_writer = csv.DictWriter(login_file, fieldnames=login_data.keys())
                if not login_exists:
                    login_writer.writeheader()
                login_writer.writerow(login_data)
                print(f"Login data written to {Alogin_file_path}: {login_data}")  # Debugging statement

        return redirect(url_for("index"))  # Redirects back to the index page

    return render_template("signup.html")  # Renders the sign-up form

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        print("No file part in request.")  # Debugging statement
        return redirect(request.url)

    files = request.files.getlist("file")

    if not files:
        print("No files selected.")  # Debugging statement
        return redirect(request.url)

    merged_filename = request.form.get("merged_filename")
    if not merged_filename:
        print("No merged filename provided.")  # Debugging statement
        return redirect(request.url)

    merged_filename = secure_filename(merged_filename) + ".pdf"

    filenames = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            filenames.append(file_path)
            print(f"File saved: {file_path}")  # Debugging statement

    if filenames:
        merger_pdf(filenames)
        merged_file_path = os.path.join(app.config["MERGED_FOLDER"], merged_filename)
        os.rename(os.path.join(app.config["MERGED_FOLDER"], "merger_output.pdf"), merged_file_path)
        print(f"Merged file saved: {merged_file_path}")  # Debugging statement
        return send_from_directory(app.config["MERGED_FOLDER"], merged_filename, as_attachment=True)
    else:
        print("No valid files to merge.")  # Debugging statement
        return redirect(request.url)



if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, redirect, url_for, send_from_directory, render_template, session, jsonify
import os
import csv
from werkzeug.utils import secure_filename
import modules

app = Flask(__name__)
app.secret_key = "my_session_key"

app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MERGED_FOLDER"] = "merged"
app.config["ALLOWED_EXTENSIONS"] = {"pdf"}

# Ensure upload and merged folders exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["MERGED_FOLDER"], exist_ok=True)

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
    fn_dynamic = session.get("fn_dynamic", "none")
    ln_dynamic = session.get("ln_dynamic", "none")
    un_dynamic = session.get("un_dynamic", "none")
    email_dynamic = session.get("email_dynamic", "none")
    pw_dynamic = session.get("pw_dynamic", "none")

    return render_template("profile.html",
                           fn_dynamic=fn_dynamic,
                           ln_dynamic=ln_dynamic,
                           un_dynamic=un_dynamic,
                           email_dynamic=email_dynamic,
                           pw_dynamic=pw_dynamic
                           )


@app.route('/update_user', methods=['POST'])
def update_user():
    try:
        updated_data = request.json
        original_email = session.get('email_dynamic')  # Retrieve original email from session
        original_username = session.get("un_dynamic")
        if not original_email:
            return jsonify({'error': 'Original email is required for update.'}), 400

        csv_adminFile = "admin.csv"
        csv_loginFile = "login_data.csv"
        rows = []
        login_rows = []
        user_updated = False

        # Read admin data
        with open(csv_adminFile, 'r') as admin_file:
            csv_reader = csv.DictReader(admin_file)
            rows = [row for row in csv_reader]  # Read all rows into memory

        # Read login data
        with open(csv_loginFile, 'r') as login_file:
            csv_loginReader = csv.DictReader(login_file)
            login_rows = [row for row in csv_loginReader]  # Read all rows into memory

        # Update admin data
        for row in rows:
            if row["username"] == original_username:
                # Update the user information
                row['first_name'] = updated_data['firstName']
                row['last_name'] = updated_data['lastName']
                row['username'] = updated_data['username']
                row['email'] = updated_data['email']
                row['password'] = updated_data['password']
                user_updated = True
                break  # Exit loop once we update the row

        # Update login data
        for login_row in login_rows:
            if login_row["username"] == original_username:
                login_row['username'] = updated_data['username']
                login_row['password'] = updated_data['password']
                break  # Exit loop once we update the row

        if user_updated:
            # Write updated admin data back to file
            with open(csv_adminFile, 'w', newline='') as file:
                fieldnames = ['first_name', 'last_name', 'username', 'email', 'password']
                csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
                csv_writer.writeheader()
                csv_writer.writerows(rows)

            # Write updated login data back to file
            with open(csv_loginFile, 'w', newline='') as login_file:
                fieldnames = ['username', 'password']
                csv_writer = csv.DictWriter(login_file, fieldnames=fieldnames)
                csv_writer.writeheader()
                csv_writer.writerows(login_rows)

            # Update session data
            session['fn_dynamic'] = updated_data['firstName']
            session['ln_dynamic'] = updated_data['lastName']
            session['un_dynamic'] = updated_data['username']
            session['email_dynamic'] = updated_data['email']
            session['pw_dynamic'] = updated_data['password']

            return jsonify({'message': 'User info updated successfully!'})
        else:
            return jsonify({'error': 'User not found.'}), 404

    except Exception as e:
        print(f"Error: {e}")  # This will log the error in the Flask console
        return jsonify({'error': 'An error occurred while updating the user info.'}), 500

@app.route("/login", methods=["GET", "POST"])
def login_page():

    if request.method == "POST":
        try_login = [request.form.get("login_un"), request.form.get("login_password")]

        login_file_path = "login_data.csv"
        admin_file_path = "admin.csv"

        if os.path.isfile(admin_file_path):
            with open(admin_file_path, "r", newline="", encoding="utf-8") as Ladmin_file:
                admin_rows = csv.reader(Ladmin_file)
                next(admin_rows)  # Skip the header row if there is one

                for row in admin_rows:
                    available_login = [row[2], row[4]]
                    if try_login == available_login:
                        session.pop("error", None)# Clear any existing error messages
                        ########################
                        session["logged_in"]=True
                        ########################
                        modules.profile_data(row) # Stores the profile data for the profile page
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

        re_password=request.form.get("signup_re_password")

        # Define the path to the CSV file
        Aadmin_file_path = "admin.csv"
        Alogin_file_path = "login_data.csv"

        # Write user_data to CSV file
        admin_exists = os.path.isfile(Aadmin_file_path)
        with open(Aadmin_file_path, mode="a", newline="", encoding="utf-8") as admin_append_file:
            # newline - ensures blank lines are handled consistently between platforms
            admin_writer = csv.DictWriter(admin_append_file, fieldnames=user_data.keys())
            # Write header if file is empty
            if not admin_exists:
                admin_writer.writeheader()


            with open(Aadmin_file_path, mode="r", newline="", encoding="utf-8") as admin_read_file:
                admin_check = csv.reader(admin_read_file)
                try:
                    next(admin_check)
                except StopIteration:
                    pass

                eroare=""
                write = True

                if modules.is_user_registered(user_data,admin_check):
                    pass
                else:
                    eroare =eroare + "Username Or Email Already Registered" +"\n"
                    write=False

                if modules.is_valid_email_syntax(user_data["email"]):
                    pass
                else:
                    eroare = eroare + "Invalid Email" +"\n"
                    write=False

                if modules.pass_too_short(user_data["password"]):
                    pass
                else:
                    eroare = eroare + "Password Too Short" +"\n"
                    write=False

                if modules.repeat_password(user_data["password"],re_password):
                    pass
                else:
                    eroare=eroare+"Passwords Don't Match"+"\n"
                    write=False


                if write==True:
                    admin_writer.writerow(user_data)
                else:
                    session["error"]=eroare
                    return redirect(url_for("signup_page"))

            login_exists = os.path.isfile(Alogin_file_path)
            with open(Alogin_file_path, "a", newline="", encoding="utf-8") as login_file:
                login_writer = csv.DictWriter(login_file, fieldnames=login_data.keys())
                if not login_exists:
                    login_writer.writeheader()
                login_writer.writerow(login_data)

        session["logged_in"] = True
        session["fn_dynamic"] = user_data["first_name"]
        session["ln_dynamic"] = user_data["last_name"]
        session["un_dynamic"] = user_data["username"]
        session["email_dynamic"] = user_data["email"]
        session["pw_dynamic"] = user_data["password"]

        return redirect(url_for("index"))  # Redirects back to the index page

    error = session.pop("error", None)
    return render_template("signup.html", error=error)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        print("No file part in request.")  # Debugging statement
        return redirect(request.url)

    files = request.files.getlist("file")

    if not files:
        print("No files selected.")  # Debugging statement
        return redirect(request.url)

    merged_filename = modules.get_merged_name(request.form.get("merged_filename"))

    filenames = []
    for file in files:
        if file and modules.allowed_file(file.filename, app.config["ALLOWED_EXTENSIONS"]):
            file_path=modules.get_filepaths(file, app.config["UPLOAD_FOLDER"])
            filenames.append(file_path)

    if filenames:
        modules.merger_pdf(filenames)
        merged_file_path = os.path.join(app.config["MERGED_FOLDER"], merged_filename)
        os.rename(os.path.join(app.config["MERGED_FOLDER"], "merger_output.pdf"), merged_file_path)
        print(f"Merged file saved: {merged_file_path}")  # Debugging statement
        return send_from_directory(app.config["MERGED_FOLDER"], merged_filename, as_attachment=True)
    else:
        print("No valid files to merge.")  # Debugging statement
        return redirect(request.url)

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, redirect, url_for, send_from_directory, render_template, session, jsonify, send_file
import os
import csv
import modules
import zipfile
import requests
from werkzeug.utils import secure_filename
import mysql.connector


app = Flask(__name__)
app.secret_key = "my_session_key"


app.config["SCHEMA_QUERY"] = "queries/create_schema.sql"
app.config["USERS_TABLE_QUERY"] = "queries/create_users.sql"
app.config["INSERT_USERS"] = "queries/insert_into_users.sql"
app.config["PROFILE_INFO"] = "queries/profile_info.sql"

app.config["UPLOAD_FOLDER"] = "uploads"
app.config["OUTPUT_FOLDER"] = "output"
app.config["ALLOWED_EXTENSIONS"] = {"pdf"}

# Ensure upload and merged folders exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)


try:
    myDatabase = modules.sql_connection()
    mycursor = myDatabase.cursor()
except mysql.connector.Error as err:
    print(f"Database connection error:{err}")

with open(app.config["USERS_TABLE_QUERY"], "r") as query:
    users_creation=query.read()

with open(app.config["SCHEMA_QUERY"], "r") as query:
    schema_creation=query.read()

mycursor.execute(schema_creation)
mycursor.execute(users_creation)

myDatabase.commit()
mycursor.close()
myDatabase.close()

@app.route("/")
def index():
    modules.clear_directory(app.config["UPLOAD_FOLDER"])
    modules.clear_directory(app.config["OUTPUT_FOLDER"])
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
            myDatabase = modules.sql_connection()
            mycursor = myDatabase.cursor()
        except mysql.connector.Error as err:
            print(f"Database connection error: {err}")
            return jsonify({'error': 'Failed to connect to the database.'}), 500

        try:
            with open("queries/update_user.sql", "r") as query:
                update_user_query = query.read()

            updated_data = request.json
            original_username = session.get("un_dynamic")

            if not original_username:
                raise ValueError("Original username not found in session.")

            update_info = (
                updated_data.get("username"),
                updated_data.get('password'),
                updated_data.get('email'),
                updated_data.get('firstName'),
                updated_data.get('lastName'),
                original_username
            )

            mycursor.execute(update_user_query, update_info)
            myDatabase.commit()

            # Update session data
            session['fn_dynamic'] = updated_data.get('firstName')
            session['ln_dynamic'] = updated_data.get('lastName')
            session['un_dynamic'] = updated_data.get('username')
            session['email_dynamic'] = updated_data.get('email')
            session['pw_dynamic'] = updated_data.get('password')

            return jsonify({'message': 'User info updated successfully!'})

        except mysql.connector.Error as err:
            myDatabase.rollback()
            print(f"SQL execution error: {err}")
            return jsonify({'error': 'An error occurred while updating the user info.'}), 500

        except ValueError as ve:
            print(f"Value error: {ve}")
            return jsonify({'error': str(ve)}), 400

        except Exception as e:
            myDatabase.rollback()
            print(f"Unexpected error: {e}")
            return jsonify({'error': 'An unexpected error occurred.'}), 500

        finally:
            mycursor.close()
            myDatabase.close()

@app.route("/login", methods=["GET", "POST"])
def login_page():
    try:
        myDatabase = modules.sql_connection()
    except mysql.connector.Error as err:
        print(f"Error :{err}")

    mycursor = myDatabase.cursor()
    mycursor.execute("SELECT username, password FROM users")
    user_list = mycursor.fetchall()


    if request.method == "POST":
        try_login = (request.form.get("login_un"), request.form.get("login_password"))

        with open(app.config["PROFILE_INFO"], "r") as query:
            profile_query = query.read()

        for user_credentials in user_list:
            if user_credentials == try_login:
                session.pop("error", None)  # Clear any existing error messages
                session["logged_in"] = True

                mycursor.execute(profile_query, user_credentials)
                profile_data = mycursor.fetchall()

                modules.profile_data(profile_data[0])
                mycursor.close()
                myDatabase.close()
                return redirect(url_for("index"))

        # Set an error message in session if login fails
        session["error"] = "Invalid username or password"
        return redirect(url_for("login_page"))

    # For GET requests, or if login fails, render the login page
    return render_template("login.html", error=session.pop("error", None))

@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    try:
        myDatabase = modules.sql_connection()
    except mysql.connector.Error as err:
        print(f"Error :{err}")

    mycursor = myDatabase.cursor()

    with open(app.config["INSERT_USERS"], "r") as query:
        insert_user = query.read()

    if request.method == "POST":
        user_data = {
            "first_name": request.form.get("signup_fn"),
            "last_name": request.form.get("signup_ln"),
            "username": request.form.get("signup_un"),
            "email": request.form.get("signup_email"),
            "password": request.form.get("signup_password"),
        }

        re_password=request.form.get("signup_re_password")

        eroare=""
        write = True

        mycursor.execute("SELECT username, email FROM users")
        admin_check = mycursor.fetchall()

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
            print("Am reusit?")
            print((user_data['username'],user_data['password'],user_data['email'],user_data['first_name'],user_data['last_name']))
            mycursor.execute(insert_user, (
                                    user_data['username'],
                                    user_data['password'],
                                    user_data['email'],
                                    user_data['first_name'],
                                    user_data['last_name'])
                             )
            myDatabase.commit()
            mycursor.close()
            myDatabase.close()
        else:
            session["error"]=eroare
            return redirect(url_for("signup_page"))

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

    merged_filename = modules.get_pdf_name(request.form.get("merged_filename"))

    filenames = []
    for file in files:
        if file and modules.allow_pdf(file.filename, app.config["ALLOWED_EXTENSIONS"]):
            file_path = modules.get_filepaths(file, app.config["UPLOAD_FOLDER"])
            filenames.append(file_path)

    if filenames:
        try:
            modules.merger_pdf(filenames, app.config["OUTPUT_FOLDER"])
            merged_file_path = os.path.join(app.config["OUTPUT_FOLDER"], merged_filename)
            temp_merged_path = os.path.join(app.config["OUTPUT_FOLDER"], "merger_output.pdf")

            if os.path.exists(temp_merged_path):
                os.rename(temp_merged_path, merged_file_path)
                print(f"Merged file saved: {merged_file_path}")  # Debugging statement
            else:
                print(f"Temporary merged file not found: {temp_merged_path}")  # Debugging statement

            modules.clear_directory(app.config["UPLOAD_FOLDER"])
            return send_from_directory(app.config["OUTPUT_FOLDER"], merged_filename, as_attachment=True)
        except Exception as e:
            print(f"Error during file processing: {e}")  # Debugging statement
            return redirect(request.url)
    else:
        print("No valid files to merge.")  # Debugging statement
        return redirect(request.url)

@app.route("/Convert", methods=["POST", "GET"])
def render_wordFiles():

    if request.method == "POST":
        # Debugging statements
        print("Received POST request.")
    logged_in = session.get("logged_in")

    if "file" not in request.files:
        print("No file part in request.")  # Debugging statement
        return redirect(request.url)

    files = request.files.getlist("file")
    file_names = [file.filename for file in files]
    sorted_names = modules.natural_sort(file_names)

    if file_names[0].lower().endswith((".docx", ".doc")):
        data_types = ".docx, .doc"
    elif file_names[0].lower().endswith((".xlsx", ".xls")):
        data_types = ".xlsx, .xls"
    elif file_names[0].lower().endswith((".pptx", ".ppt")):
        data_types = ".pptx, .ppt"
    elif file_names[0].lower().endswith((".jpeg", ".jpg")):
        data_types = ".jpeg, .jpg"
    elif file_names[0].lower().endswith(".gif"):
        data_types = ".gif"
    elif file_names[0].lower().endswith(".png"):
        data_types = ".png"
    elif file_names[0].lower().endswith(".bmp"):
        data_types = ".bmp"

    if not files:
        print("No files selected.")
        return redirect(request.url)

    for file in files:
        if file:
            file_path = modules.get_filepaths(file, app.config["UPLOAD_FOLDER"])
        else:
            print(f"Invalid file format: {file.filename}")

    file_count=len(os.listdir(app.config["UPLOAD_FOLDER"]))
    print(os.listdir(app.config["UPLOAD_FOLDER"]))

    return render_template("Convert.html", logged_in=logged_in,
                                                            file_names=sorted_names,
                                                            data_types=data_types,
                                                            file_count=file_count)


@app.route("/convertWord", methods=["POST", "GET"])
def upload_word_file():
    names = request.form.getlist("file_names[]")
    print(f"New names: {names}")

    # List files in the upload directory and filter out temp files
    files = [f for f in os.listdir(app.config["UPLOAD_FOLDER"]) if not f.startswith('~$')]
    print(f"Contents of the temp dir: {files}")

    # Create a dictionary to map the original filenames to the new names
    file_rename_map = dict(zip(files, names))
    print(file_rename_map)

    output_folder = app.config["OUTPUT_FOLDER"]
    os.makedirs(output_folder, exist_ok=True)

    converted_files = []

    if names:
        for file in files:
            try:
                # Get the corresponding new name from the map
                file_name = file_rename_map.get(file)
                secured_name = secure_filename(file_name)

                docx_file_path = os.path.join(app.config["UPLOAD_FOLDER"], file)

                # Convert file and handle name correction
                modules.convert_file_to_pdf(docx_file_path, secured_name, output_folder)

                # Rename the file if necessary and check for conversion output
                if secured_name.lower().endswith(('.docx', '.xlsx', '.pptx', '.jpeg')):
                    cleaned_name = secured_name[:-5] + ".pdf"
                elif secured_name.lower().endswith(('.doc', '.xls', '.ppt', '.jpg', '.png', '.bmp', '.gif')):
                    cleaned_name = secured_name[:-4] + ".pdf"
                else:
                    cleaned_name = secured_name + ".pdf"

                output_file_path = os.path.join(output_folder, cleaned_name)

                if os.path.exists(output_file_path):
                    converted_files.append(output_file_path)
                    print(f"Conversion successful for {file_name}")
                else:
                    print(f"Converted file not found for {file_name}")

            except Exception as e:
                print(f"Error during conversion for {file_name}: {e}")
                return redirect(request.url)

        print(f"Converted files: {converted_files}")

        # Handle multiple or single files for download
        if len(converted_files) > 1:
            zip_filename = "converted_files.zip"
            zip_path = os.path.join(output_folder, zip_filename)
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for file in converted_files:
                    zipf.write(file, os.path.basename(file))
            print(f"Returning zip file: {zip_path}")
            return send_file(zip_path, as_attachment=True, mimetype='application/zip')
        elif converted_files:
            print(f"Returning single file: {converted_files[0]}")
            modules.clear_directory(app.config["UPLOAD_FOLDER"])
            return send_file(converted_files[0], as_attachment=True)
        else:
            print("No valid files were converted.")
            return redirect(request.url)

    else:
        print("No file names provided.")
        return redirect(request.url)


@app.route('/addFile', methods=['POST'])
def add_file():

    print("Activated Path")
    if 'file' not in request.files:
        return 'No file part', 400

    files = request.files.getlist('file')
    file_names = [file.filename for file in files]
    file_paths = []

    for file in files:
        if file:
            try:
                file_path = modules.get_filepaths(file, app.config['UPLOAD_FOLDER'])
                file_paths.append(file_path)
            except Exception as e:
                return f"An error occurred: {e}", 500

    file_count = len(os.listdir(app.config["UPLOAD_FOLDER"]))
    sorted_names = modules.natural_sort(os.listdir(app.config['UPLOAD_FOLDER']))

    if sorted_names[0].lower().endswith((".docx", ".doc")):
        data_types = ".docx, .doc"
    elif sorted_names[0].lower().endswith((".xlsx", ".xls")):
        data_types = ".xlsx, .xls"
    elif sorted_names[0].lower().endswith((".pptx", ".ppt")):
        data_types = ".pptx, .ppt"
    elif sorted_names[0].lower().endswith((".jpeg", ".jpg")):
        data_types = ".jpeg, .jpg"
    elif sorted_names[0].lower().endswith(".gif"):
        data_types = ".gif"
    elif sorted_names[0].lower().endswith(".png"):
        data_types = ".png"
    elif sorted_names[0].lower().endswith(".bmp"):
        data_types = ".bmp"

    logged_in = session.get("logged_in")

    print(f"Files uploaded successfully: {file_paths}")  # Debug statement
    return render_template("Convert.html", logged_in=logged_in,
                                                             file_names=sorted_names,
                                                             data_types=data_types,
                                                             file_count=file_count)


@app.route('/deleteFile', methods=['POST'])
def delete_file():
    data = request.get_json()
    file_name = data.get('fileName')
    secured_filename= secure_filename(file_name)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secured_filename)

    print(f"Attempting to delete file: {file_path}")  # Debugging statement

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Successfully deleted file: {file_path}")  # Debugging statement
            remaining_files = len(os.listdir(app.config['UPLOAD_FOLDER']))
            return jsonify({'success': True, 'file_count': remaining_files})



        except Exception as e:
            print(f"Error deleting file: {e}")  # Debugging statement
            return jsonify({'success': False, 'message': 'Error deleting file'}), 500
    else:
        print(f"File not found: {file_path}")  # Debugging statement
        return jsonify({'success': False, 'message': 'File not found'}), 404


if __name__ == "__main__":
    app.run(debug=True)

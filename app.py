from flask import (
      Flask, request, redirect, url_for,
      send_from_directory, render_template,
      session, jsonify, send_file
)
import os
import modules
import zipfile
from werkzeug.utils import secure_filename
import mysql.connector
import bcrypt
import threading


app = Flask(__name__)
app.secret_key = "my_session_key"


app.config["SCHEMA_QUERY"] = "queries/Create_queries/create_schema.sql"
app.config["USERS_TABLE_QUERY"] = "queries/Create_queries/create_users.sql"
app.config["SUBSCRIPTIONS_TABLE_QUERY"] = "queries/Create_queries/create_subscriptions.sql"

app.config["UPDATE_USERS"] = "queries/Update_queries/update_user.sql"
app.config["INSERT_USERS"] = "queries/Update_queries/insert_into_users.sql"
app.config["BUY_7DAYPREMIUM"] = "queries/Update_queries/buy_7dayPremium_query.sql"
app.config["DELETE_USER"] = "queries/Update_queries/delete_user.sql"
app.config["DELETE_SUBSCRIPTION"] = "queries/Update_queries/delete_subscription.sql"

app.config["PROFILE_INFO"] = "queries/Get_info_queries/profile_info.sql"
app.config["LOGIN_INFO"] = "queries/Get_info_queries/get_login_info.sql"

app.config["UPLOAD_FOLDER"] = "uploads"
app.config["OUTPUT_FOLDER"] = "output"
app.config["ALLOWED_EXTENSIONS"] = {"pdf"}


try:
    myDatabase = modules.sql_connection()
    mycursor = myDatabase.cursor()

    with open(app.config["USERS_TABLE_QUERY"], "r") as query:
        mycursor.execute(query.read())

    with open(app.config["SCHEMA_QUERY"], "r") as query:
        mycursor.execute(query.read())

    with open(app.config["SUBSCRIPTIONS_TABLE_QUERY"], "r") as query:
        mycursor.execute(query.read())

    myDatabase.commit()

except mysql.connector.Error as err:
    print(f"Database error: {err}")

finally:
    mycursor.close()
    myDatabase.close()

@app.route("/")
def index():
    try:
        usable_id = session.get("user_id", "none")

        upload_folder = usable_id+"_"+app.config["UPLOAD_FOLDER"]
        output_folder = usable_id + "_"+app.config["OUTPUT_FOLDER"]

        modules.deferred_cleanup(upload_folder, output_folder)
    except FileNotFoundError:
        pass

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
    points_dynamic = session.get("points_dynamic", "none")
    upgrade_successful = session.pop('upgrade_successful', None)

    return render_template("profile.html",
                           fn_dynamic=fn_dynamic,
                           ln_dynamic=ln_dynamic,
                           un_dynamic=un_dynamic,
                           email_dynamic=email_dynamic,
                           points_dynamic=points_dynamic,
                           upgrade_successful=upgrade_successful
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
            with open(app.config["UPDATE_USERS"], "r") as query:
                update_user_query = query.read()

            updated_data = request.json
            original_username = session.get("un_dynamic")

            if not original_username:
                raise ValueError("Original username not found in session.")

            valid=True
            eroare=""

            if not modules.is_valid_email_syntax(updated_data.get('email')):
                eroare += "Invalid Email\n"
                valid = False

            if valid == True:
                update_info = (
                    updated_data.get("username"),
                    updated_data.get('email'),
                    updated_data.get('firstName'),
                    updated_data.get('lastName'),
                    original_username
                )

                mycursor.execute(update_user_query, update_info)
                myDatabase.commit()

                session['fn_dynamic'] = updated_data.get('firstName')
                session['ln_dynamic'] = updated_data.get('lastName')
                session['un_dynamic'] = updated_data.get('username')
                session['email_dynamic'] = updated_data.get('email')

                return jsonify({'message': 'User info updated successfully!'})

            else:
                return render_template("signup.html", error=eroare)

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
        mycursor = myDatabase.cursor()

        with open(app.config["LOGIN_INFO"], 'r') as query:
            mycursor.execute(query.read())
            user_list = mycursor.fetchall()

        if request.method == "POST":
            user_log = request.form.get("login_un")
            pass_log = request.form.get("login_password").encode("UTF-8")

            with open(app.config["PROFILE_INFO"], "r") as query:
                profile_query = query.read()

            for user_credentials in user_list:
                stored_hashed_password = user_credentials[1].encode("UTF-8")

                if user_credentials[0] == user_log and bcrypt.checkpw(pass_log, stored_hashed_password):
                    session.pop("error", None)
                    session["logged_in"] = True

                    mycursor.execute("SELECT id FROM users WHERE username = %s", (user_log,))
                    login_id = mycursor.fetchall()

                    session["user_id"] = str(login_id[0][0])

                    mycursor.execute( profile_query, (str(login_id[0][0]),) )
                    profile_data = mycursor.fetchall()
                    modules.profile_data(profile_data[0])

                    return redirect(url_for("index"))

            session["error"] = "Invalid username or password"
            return redirect(url_for("login_page"))

    finally:
        mycursor.close()
        myDatabase.close()

    return render_template("login.html", error=session.pop("error", None))

@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    try:
        myDatabase = modules.sql_connection()
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return render_template("signup.html", error="Database connection failed")

    try:
        mycursor = myDatabase.cursor()
    except mysql.connector.Error as err:
        print(f"Cursor creation error: {err}")
        return render_template("signup.html", error="Unable to process request")

    try:
        with open(app.config["INSERT_USERS"], "r") as query:
            insert_user = query.read()
    except FileNotFoundError as fnf_error:
        print(f"File not found: {fnf_error}")
        return render_template("signup.html", error="Internal server error")
    except Exception as e:
        print(f"Error reading query file: {e}")
        return render_template("signup.html", error="Internal server error")

    if request.method == "POST":
        crypted_pw = bcrypt.hashpw(request.form.get("signup_password").encode("UTF-8"), bcrypt.gensalt(rounds=14))

        user_data = {
            "first_name": request.form.get("signup_fn"),
            "last_name": request.form.get("signup_ln"),
            "username": request.form.get("signup_un"),
            "email": request.form.get("signup_email"),
            "password": crypted_pw,
            "gender": request.form.get("gender")
        }

        re_password = request.form.get("signup_re_password")
        eroare = ""
        write = True

        try:
            mycursor.execute("SELECT username, email FROM users")
            admin_check = mycursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Database query error: {err}")
            return render_template("signup.html", error="Failed to validate user information")

        if modules.is_user_registered(user_data, admin_check):
            pass
        else:
            eroare += "Username or Email already registered\n"
            write = False

        if modules.is_valid_email_syntax(user_data["email"]):
            pass
        else:
            eroare += "Invalid Email\n"
            write = False

        if modules.repeat_password(request.form.get("signup_password"), re_password):
            pass
        else:
            eroare += "Passwords don't match\n"
            write = False

        if write:
            try:
                mycursor.execute("START TRANSACTION")

                mycursor.execute(insert_user, (
                    user_data['username'],
                    user_data['password'],
                    user_data['email'],
                    user_data['first_name'],
                    user_data['last_name'],
                    user_data['gender'],
                ))

                mycursor.execute("SET @user_id = LAST_INSERT_ID()")

                mycursor.execute("""
                    INSERT INTO subscriptions (user_id)
                    VALUES (@user_id)
                """)
                myDatabase.commit()

                mycursor.execute("SELECT id FROM users WHERE username = %s", (user_data['username'],))
                signup_id = mycursor.fetchall()
                session["user_id"] = str(signup_id[0][0])

            except mysql.connector.Error as err:
                print(f"Insert user error: {err}")
                mycursor.close()
                myDatabase.close()
                return render_template("signup.html", error="User registration failed")

            mycursor.close()
            myDatabase.close()
        else:
            session["error"] = eroare
            return redirect(url_for("signup_page"))

        session["logged_in"] = True
        session["fn_dynamic"] = user_data["first_name"]
        session["ln_dynamic"] = user_data["last_name"]
        session["un_dynamic"] = user_data["username"]
        session["email_dynamic"] = user_data["email"]
        session["pw_dynamic"] = user_data["password"]
        session["points_dynamic"] = 0

        return redirect(url_for("index"))

    error = session.pop("error", None)
    return render_template("signup.html", error=error)

@app.route("/mergePDF", methods=["POST"])
def upload_file():
    usable_id = session.get("user_id", "none")

    upload_folder = usable_id+"_"+app.config["UPLOAD_FOLDER"]
    output_folder = usable_id+"_"+app.config["OUTPUT_FOLDER"]

    os.makedirs(upload_folder, exist_ok = True)
    os.makedirs(output_folder, exist_ok = True)

    if "file" not in request.files:
        print("No file part in request.")
        return redirect(request.url)

    files = request.files.getlist("file")

    if not files:
        print("No files selected.")
        return redirect(request.url)

    merged_filename = modules.get_pdf_name(request.form.get("merged_filename"))

    filenames = []
    for file in files:
        if file and modules.allow_pdf(file.filename, app.config["ALLOWED_EXTENSIONS"]):
            file_path = modules.get_filepaths(file, upload_folder)
            filenames.append(file_path)

    if filenames:
        try:
            modules.merger_pdf(filenames, output_folder)
            merged_file_path = os.path.join(output_folder, merged_filename)
            temp_merged_path = os.path.join(output_folder, "merger_output.pdf")

            if os.path.exists(temp_merged_path):
                os.rename(temp_merged_path, merged_file_path)
                print(f"Merged file saved: {merged_file_path}")
            else:
                print(f"Temporary merged file not found: {temp_merged_path}")

            try:
                myDatabase = modules.sql_connection()
                mycursor = myDatabase.cursor()
                mycursor.execute("UPDATE subscriptions SET points = points + 10 WHERE user_id = %s", (usable_id,))
                mycursor.execute("SELECT points FROM subscriptions WHERE user_id = %s", (usable_id,))
                session["points_dynamic"] = str(mycursor.fetchall()[0][0])
                myDatabase.commit()
                print("points added!")
            except Exception as e:
                return jsonify({'error': str(e)}), 500

            finally:
                if mycursor:
                    mycursor.close()
                if myDatabase:
                    myDatabase.close()

            cleanup_thread = threading.Thread(target=modules.deferred_cleanup, args=(upload_folder,
                                                                                     output_folder))
            cleanup_thread.start()

            return send_from_directory(usable_id+"_"+app.config["OUTPUT_FOLDER"], merged_filename, as_attachment=True)
        except Exception as e:
            print(f"Error during file processing: {e}")
            return redirect(request.url)
    else:
        print("No valid files to merge.")
        return redirect(request.url)

@app.route("/convertPage", methods=["POST", "GET"])
def render_wordFiles():
    if request.method == "POST":
        print("Received POST request.")

    form_name = request.form.get('form_name')
    session["wanted_file_type"] = form_name
    print(session.get("wanted_file_type"))

    logged_in = session.get("logged_in")

    if "file" not in request.files:
        print("No file part in request.")
        return redirect(request.url)

    usable_id = session.get("user_id", "none")
    upload_folder = usable_id + "_" + app.config["UPLOAD_FOLDER"]
    output_folder = usable_id + "_" + app.config["OUTPUT_FOLDER"]

    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    files = request.files.getlist("file")
    file_names = [file.filename for file in files]
    sorted_names = modules.natural_sort(file_names)

    if file_names[0].lower().endswith((".docx", ".doc")):
        data_types = ".docx, .doc"
    elif file_names[0].lower().endswith((".xlsx", ".xls")):
        data_types = ".xlsx, .xls"
    elif file_names[0].lower().endswith((".pptx", ".ppt", ".pps")):
        data_types = ".pptx, .ppt, .pps"
    elif file_names[0].lower().endswith((".jpeg", ".jpg")):
        data_types = ".jpeg, .jpg"
    elif file_names[0].lower().endswith(".gif"):
        data_types = ".gif"
    elif file_names[0].lower().endswith(".png"):
        data_types = ".png"
    elif file_names[0].lower().endswith(".bmp"):
        data_types = ".bmp"
    elif file_names[0].lower().endswith(".pdf"):
        data_types = ".pdf"

    if not files:
        print("No files selected.")
        return redirect(request.url)

    for file in files:
        if file:
            file_path = modules.get_filepaths(file, upload_folder)
        else:
            print(f"Invalid file format: {file.filename}")

    file_count=len(os.listdir(upload_folder))

    for i in range(len(sorted_names)):
        try:
            if sorted_names[i].split(".")[0] == sorted_names[i+1].split(".")[0] + " - Copy":
                print("YES")
                sorted_names[i], sorted_names[i+1] = sorted_names[i+1], sorted_names[i]
        except IndexError:
            break

    return render_template("convert.html", logged_in=logged_in,
                                                            file_names=sorted_names,
                                                            data_types=data_types,
                                                            file_count=file_count)


@app.route("/convert", methods=["POST", "GET"])
def upload_word_file():
    names = request.form.getlist("file_names[]")

    usable_id = session.get("user_id", "none")

    wanted_file_type = session.get("wanted_file_type")

    upload_folder = usable_id + "_" + app.config["UPLOAD_FOLDER"]
    output_folder = usable_id + "_" + app.config["OUTPUT_FOLDER"]

    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    # List files in the upload directory and filter out temp files
    files = [f for f in os.listdir(upload_folder) if not f.startswith('~$')]
    print(f"Contents of the temp dir: {files}")

    # Create a dictionary to map the original filenames to the new names
    file_rename_map = dict(zip(files, names))
    print(file_rename_map)

    os.makedirs(output_folder, exist_ok=True)

    converted_files = []
    if wanted_file_type == ".pdf":
        if names:
            for file in files:
                try:
                    # Get the corresponding new name from the map
                    file_name = file_rename_map.get(file)

                    if file_name ==  "":
                        file_name = "convertedPDF"

                    secured_name = secure_filename(file_name)

                    docx_file_path = os.path.join(upload_folder, file)

                    # Convert file and handle name correction
                    modules.convert_file_to_pdf(docx_file_path, secured_name, output_folder)

                    # Rename the file if necessary and check for conversion output
                    if secured_name.lower().endswith(('.docx', '.xlsx', '.pptx', '.jpeg')):
                        cleaned_name = secured_name[:-5] + ".pdf"
                    elif secured_name.lower().endswith(('.doc', '.xls', '.ppt', '.pps', '.jpg', '.png', '.bmp', '.gif')):
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

            usable_id = session.get("user_id")
            try:
                myDatabase = modules.sql_connection()  # Establish a database connection
                mycursor = myDatabase.cursor()
                mycursor.execute("UPDATE subscriptions SET points = points + 10 WHERE user_id = %s", (usable_id,))
                mycursor.execute("SELECT points FROM subscriptions WHERE user_id = %s", (usable_id,))
                session["points_dynamic"] = str(mycursor.fetchall()[0][0])
                myDatabase.commit()  # Commit the changes
                print("points added!")
            except Exception as e:
                return jsonify({'error': str(e)}), 500  # Handle any database errors

            finally:
                if mycursor:
                    mycursor.close()  # Ensure cursor is closed
                if myDatabase:
                    myDatabase.close()  # Ensure database connection is closed

            # Handle multiple or single files for download
            if len(converted_files) > 1:
                zip_filename = "converted_files.zip"
                zip_path = os.path.join(output_folder, zip_filename)
                with zipfile.ZipFile(zip_path, "w") as zipf:
                    for file in converted_files:
                        zipf.write(file, os.path.basename(file))

                cleanup_thread = threading.Thread(target=modules.deferred_cleanup, args=(upload_folder,
                                                                                         output_folder))
                cleanup_thread.start()

                print(f"Returning zip file: {zip_path}")
                return send_file(zip_path, as_attachment=True, mimetype='application/zip')
            elif converted_files:

                cleanup_thread = threading.Thread(target=modules.deferred_cleanup, args=(upload_folder,
                                                                                         output_folder))
                cleanup_thread.start()

                print(f"Returning single file: {converted_files[0]}")
                return send_file(converted_files[0], as_attachment=True)
            else:
                print("No valid files were converted.")
                return redirect(request.url)

        else:
            print("No file names provided.")
            return redirect(request.url)

    else:
        if names:
            for file in files:
                try:
                    # Get the corresponding new name from the map
                    file_name = file_rename_map.get(file)

                    if file_name ==  "":
                        file_name = "convertedWord.docx"

                    secured_name = secure_filename(file_name)

                    pdf_file_path = os.path.join(upload_folder, file)

                    # Use convert_pdf_to_file for conversion
                    modules.convert_pdf_to_word(pdf_file_path, wanted_file_type, output_folder, secured_name)

                    # Construct the output filename based on the desired format
                    base_name = os.path.splitext(secured_name)[0]
                    cleaned_name = f"{base_name}{wanted_file_type}"

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

            usable_id = session.get("user_id")
            try:
                myDatabase = modules.sql_connection()  # Establish a database connection
                mycursor = myDatabase.cursor()
                mycursor.execute("UPDATE subscriptions SET points = points + 10 WHERE user_id = %s", (usable_id,))
                mycursor.execute("SELECT points FROM subscriptions WHERE user_id = %s", (usable_id,))
                session["points_dynamic"] = str(mycursor.fetchall()[0][0])
                myDatabase.commit()  # Commit the changes
                print("Points added!")
            except Exception as e:
                return jsonify({'error': str(e)}), 500  # Handle any database errors

            finally:
                if mycursor:
                    mycursor.close()  # Ensure cursor is closed
                if myDatabase:
                    myDatabase.close()  # Ensure database connection is closed

            # Handle multiple or single files for download
            if len(converted_files) > 1:
                zip_filename = "converted_files.zip"
                zip_path = os.path.join(output_folder, zip_filename)
                with zipfile.ZipFile(zip_path, "w") as zipf:
                    for file in converted_files:
                        zipf.write(file, os.path.basename(file))

                cleanup_thread = threading.Thread(target=modules.deferred_cleanup, args=(upload_folder, output_folder))
                cleanup_thread.start()

                print(f"Returning zip file: {zip_path}")
                return send_file(zip_path, as_attachment=True, mimetype='application/zip')
            elif converted_files:
                cleanup_thread = threading.Thread(target=modules.deferred_cleanup, args=(upload_folder, output_folder))
                cleanup_thread.start()

                print(f"Returning single file: {converted_files[0]}")
                return send_file(converted_files[0], as_attachment=True)
            else:
                print("No valid files were converted.")
                return redirect(request.url)

        else:
            print("No file names provided.")
            return redirect(request.url)


@app.route('/addFile', methods=['POST'])
def add_file():
    if 'file' not in request.files:
        return 'No file part', 400

    files = request.files.getlist('file')
    file_names = [file.filename for file in files]
    file_paths = []

    usable_id = session.get("user_id", "none")

    upload_folder = usable_id + "_" + app.config["UPLOAD_FOLDER"]

    os.makedirs(upload_folder, exist_ok=True)

    for file in files:
        if file:
            try:
                file_path = modules.get_filepaths(file, upload_folder)
                file_paths.append(file_path)
            except Exception as e:
                return f"An error occurred: {e}", 500

    file_count = len(os.listdir(upload_folder))
    sorted_names = modules.natural_sort(os.listdir(upload_folder))

    if sorted_names[0].lower().endswith((".docx", ".doc")):
        data_types = ".docx, .doc"
    elif sorted_names[0].lower().endswith((".xlsx", ".xls")):
        data_types = ".xlsx, .xls"
    elif sorted_names[0].lower().endswith((".pptx", ".ppt", ".pps")):
        data_types = ".pptx, .ppt, .pps"
    elif sorted_names[0].lower().endswith((".jpeg", ".jpg")):
        data_types = ".jpeg, .jpg"
    elif sorted_names[0].lower().endswith(".gif"):
        data_types = ".gif"
    elif sorted_names[0].lower().endswith(".png"):
        data_types = ".png"
    elif sorted_names[0].lower().endswith(".bmp"):
        data_types = ".bmp"
    elif sorted_names[0].lower().endswith(".pdf"):
        data_types = ".pdf"

    logged_in = session.get("logged_in")

    print(f"Files uploaded successfully: {file_paths}")  # Debug statement
    return render_template("convert.html", logged_in=logged_in,
                                                             file_names=sorted_names,
                                                             data_types=data_types,
                                                             file_count=file_count)


@app.route('/deleteFile', methods=['POST'])
def delete_file():
    data = request.get_json()
    file_name = data.get('fileName')
    secured_filename= secure_filename(file_name)

    usable_id = session.get("user_id", "none")

    upload_folder = usable_id + "_" + app.config["UPLOAD_FOLDER"]

    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, secured_filename)

    print(f"Attempting to delete file: {file_path}")  # Debugging statement

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Successfully deleted file: {file_path}")  # Debugging statement
            remaining_files = len(os.listdir(upload_folder))
            return jsonify({'success': True, 'file_count': remaining_files})

        except Exception as e:
            print(f"Error deleting file: {e}")  # Debugging statement
            return jsonify({'success': False, 'message': 'Error deleting file'}), 500
    else:
        print(f"File not found: {file_path}")  # Debugging statement
        return jsonify({'success': False, 'message': 'File not found'}), 404


@app.route("/pointsForPremium", methods=["POST"])
def premium_trial():
    usable_id = session.get("user_id")  # Get user ID from session
    print(usable_id)
    if usable_id is None:
        return jsonify({'error': 'User not logged in.'}), 403  # Handle case if user is not logged in
    try:
        myDatabase = modules.sql_connection()  # Establish a database connection
        mycursor = myDatabase.cursor()

        with open(app.config["BUY_7DAYPREMIUM"], 'r') as query:
            mycursor.execute(query.read(), (usable_id,))

        mycursor.execute("SELECT points FROM subscriptions WHERE user_id = %s", (usable_id,))
        session["points_dynamic"] = str(mycursor.fetchall()[0][0])
        myDatabase.commit()

        session['upgrade_successful'] = True

        return redirect(url_for("profile_page"))

    finally:
        if mycursor:
            mycursor.close()  # Ensure cursor is closed
        if myDatabase:
            myDatabase.close()  # Ensure database connection is closed

@app.route("/changePassword", methods=['POST'])
def change_password():
    usable_id = session.get("user_id")  # Get user ID from session
    updated_crypted_pw = bcrypt.hashpw(request.form.get("updated_password").encode("UTF-8"), bcrypt.gensalt(rounds=14))

    if usable_id is None:
        return jsonify({'error': 'User not logged in.'}), 403  # Handle case if user is not logged in
    try:

        myDatabase = modules.sql_connection()  # Establish a database connection
        mycursor = myDatabase.cursor()
        mycursor.execute("UPDATE users SET password = %s WHERE id = %s", (updated_crypted_pw, usable_id))
        myDatabase.commit()  # Commit the changes

        return '', 204

    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Handle any database errors

    finally:
        if mycursor:
            mycursor.close()  # Ensure cursor is closed
        if myDatabase:
            myDatabase.close()  # Ensure database connection is closed

@app.route("/deleteAccount", methods=['POST'])
def delete_account():
    usable_id = session.get("user_id")  # Get user ID from session
    if usable_id is None:
        return jsonify({'error': 'User not logged in.'}), 403  # Handle case if user is not logged in

    try:
        myDatabase = modules.sql_connection()  # Establish a database connection
        mycursor = myDatabase.cursor()

        # Load the delete query from the SQL file
        with open(app.config["DELETE_USER"], "r") as query:
            mycursor.execute(query.read(), (usable_id,))

        with open(app.config["DELETE_SUBSCRIPTION"], "r") as query:
            mycursor.execute(query.read(), (usable_id,))

        myDatabase.commit()  # Commit the transaction

    finally:
        if mycursor:
            mycursor.close()  # Ensure cursor is closed
        if myDatabase:
            myDatabase.close()  # Ensure database connection is closed

    session.pop("logged_in", None)  # Remove user from session
    session.pop("user_id", None)  # Remove user_id from session
    return redirect(url_for("index"))  # Redirect to the index page

if __name__ == "__main__":
    app.run(debug=True)

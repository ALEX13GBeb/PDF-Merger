from PyPDF2 import PdfMerger
from flask import session, redirect, request
from werkzeug.utils import secure_filename
import os

def merger_pdf(pdf_files):

    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    with open("merged\merger_output.pdf", "wb") as output_pdf:
        merger.write(output_pdf)

def profile_data(list):
    session["fn_dynamic"] = list[0]
    session["ln_dynamic"] = list[1]
    session["un_dynamic"] = list[2]
    session["email_dynamic"] = list[3]
    session["pw_dynamic"] = list[4]
    return (session["fn_dynamic"],session["ln_dynamic"],session["un_dynamic"],session["email_dynamic"],session["pw_dynamic"])

def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

def get_merged_name(output_file):
    merged_filename = output_file
    if not merged_filename:
        print("No merged filename provided.")  # Debugging statement
        return redirect(request.url)
    else:
        output_filename = secure_filename(merged_filename) + ".pdf"
        return output_filename

def get_filepaths(file, upload_folder):
    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    return file_path


def is_user_registered(user_data, user_database):
    for row in user_database:
        if user_data["email"] != row[3] and user_data["username"] != row[2]:
            new = True
        else:
            new = False
            session.pop("error", None)
            session["error"] = "Username or Email already registered"
            break
    return new





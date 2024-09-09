from PyPDF2 import PdfMerger
from flask import session, redirect, request
from werkzeug.utils import secure_filename
import os, shutil
import re
from docx2pdf import convert
import pythoncom

def clear_directory(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def merger_pdf(pdf_files):
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    with open("merged\merger_output.pdf", "wb") as output_pdf:
        merger.write(output_pdf)


def convert_docx_to_pdf(docx_file, rename, output_folder="merged"):
    pythoncom.CoInitialize()  # Initialize COM
    try:
        convert(docx_file, output_folder)  # Perform conversion
        first_split = os.path.splitext(docx_file)[0]
        second_split = first_split.split(os.path.sep)[-1]  # For cross-platform compatibility

        original_pdf_path = os.path.join(output_folder, second_split + ".pdf")
        new_pdf_path = os.path.join(output_folder, rename + ".pdf")

        if os.path.exists(original_pdf_path):
            os.rename(original_pdf_path, new_pdf_path)  # Rename the converted PDF
            print(f"Renamed {original_pdf_path} to {new_pdf_path}")
        else:
            print(f"File {original_pdf_path} not found.")
    finally:
        pythoncom.CoUninitialize()

def profile_data(list):
    session["fn_dynamic"] = list[0]
    session["ln_dynamic"] = list[1]
    session["un_dynamic"] = list[2]
    session["email_dynamic"] = list[3]
    session["pw_dynamic"] = list[4]
    return (session["fn_dynamic"],session["ln_dynamic"],session["un_dynamic"],session["email_dynamic"],session["pw_dynamic"])

def allow_pdf(filename, allowed_extensions="pdf"):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

def allow_word(filename, allowed_extensions="docx"):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def get_pdf_name(output_file):
    filename = output_file
    if not filename:
        print("No merged filename provided.")  # Debugging statement
        return redirect(request.url)
    else:
        output_filename = secure_filename(filename) + ".pdf"
        return output_filename

def get_filepaths(file, upload_folder):

    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    try:
        file.save(file_path)
    except Exception as e:
        print(f"Error saving file {filename}: {e}")
        raise
    return file_path


def is_user_registered(user_data, user_database):
    valid = True  # Initialize valid to True

    for row in user_database:
        if user_data["email"] == row[3] or user_data["username"] == row[2]:
            valid = False
            break

    return valid


def is_valid_email_syntax(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    popular_domains = [
        "gmail",
        "yahoo",
        "outlook",
        "hotmail",
        "icloud",
        "aol",
        "protonmail",
        "yandex",
        "zoho",
        "mail"
    ]
    parts_email = re.split(r"[@.]", email)



    if parts_email[1] in popular_domains and re.match(regex, email):
        return True
    else:

        return False

def pass_too_short(password):
    if len(password)>=8:
        return True
    else:

        return False


def password_strength(password):
    strength=0
    if len(password)>=8:
        strength+=1
    if any(char.isdigit() for char in password):
        strength += 1
    if any(char.isalpha() for char in password):
        strength += 1
    if any(not (char.isdigit() or char.isalpha()) for char in password):
        strength += 1
    return strength

def repeat_password(password, re_password):
    if password==re_password:
        return True
    else:
        return False






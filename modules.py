from PyPDF2 import PdfMerger
from flask import session, redirect, request
from werkzeug.utils import secure_filename
import os, shutil
import re
from docx2pdf import convert
import pythoncom
import time
import win32com.client as win32


def clear_directory(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                time.sleep(0.1)
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

def natural_sort(elements):
    def natural_key(text):
        # Use a regex to split the string into chunks of digits and non-digits
        return [int(chunk) if chunk.isdigit() else chunk.lower() for chunk in re.split('([0-9]+)', text)]

    return sorted(elements, key=natural_key)

def merger_pdf(pdf_files, output_folder):
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    with open(output_folder+"/merger_output.pdf", "wb") as output_pdf:
        merger.write(output_pdf)

    merger.close()


def convert_word_to_pdf(word_file, rename, output_folder):
    pythoncom.CoInitialize()

    try:
        # Get the absolute file path
        abs_word_file = os.path.abspath(word_file) # - for word file in uploads folder
        abs_output_folder = os.path.abspath(output_folder)

        # Debugging:
        print(f"Word file: {abs_word_file}")
        print(f"Rename: {rename}")
        print(f"Output folder: {abs_output_folder}")

        # Get the base name and extension
        base_name = os.path.splitext(os.path.basename(abs_word_file))[0]
        ext = os.path.splitext(abs_word_file)[1].lower()

        # Debugging:
        print(f"Base name: {base_name}")
        print(f"Extension: {ext}")

        if ext not in ['.doc', '.docx']:
            raise ValueError("Unsupported file format. Only .doc and .docx are supported.")

        print("Performing conversion...")

        # Initialize Word application
        word_app = win32.Dispatch("Word.Application")
        word_app.Visible = False

        # Open the Word file
        doc = word_app.Documents.Open(abs_word_file)

        # Define the PDF output path
        pdf_output_path = os.path.join(abs_output_folder, f"{base_name}.pdf")

        # Save as PDF
        doc.SaveAs(pdf_output_path, FileFormat=17)  # 17 is the wdFormatPDF constant

        # Close the document and Word app
        doc.Close(SaveChanges=False)
        word_app.Quit()

        # Handle renaming
        if rename.endswith(".docx"):
            new_name = rename[:-5] + ".pdf"
        elif rename.endswith(".doc"):
            new_name = rename[:-4] + ".pdf"
        else:
            new_name = rename + ".pdf"

        new_pdf_output_path = os.path.join(abs_output_folder, new_name)
        if os.path.exists(pdf_output_path):
            os.rename(pdf_output_path, new_pdf_output_path)
            print(f"Renamed {pdf_output_path} to {new_pdf_output_path}")
        else:
            print(f"Converted file {pdf_output_path} not found.")

    except Exception as e:
        print(f"Error during conversion: {e}")

    finally:
        pythoncom.CoUninitialize()


def sanitize_filename(filename):
    # Replace spaces with underscores and handle other special characters
    sanitized = re.sub(r'[^\w\s]', '', filename).replace(' ', '_')
    return sanitized


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









from PyPDF2 import PdfMerger, PdfWriter, PdfReader
from pptx import Presentation
from pdf2image import convert_from_path
from pdf2docx import Converter
from pdfplumber import open as open_pdf
from flask import session, redirect, request
from werkzeug.utils import secure_filename
import os, shutil
import re
import pythoncom
from typing import List
import comtypes.client
from PIL import Image
from reportlab.pdfgen import canvas
import tempfile
import mysql.connector
from dotenv import load_dotenv
import time

load_dotenv()

def sql_connection():
    database = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        port=os.getenv('MYSQL_PORT'),
        database=os.getenv('MYSQL_DB')
    )

    return database

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

def deferred_cleanup(directory1, directory2):
    clear_directory(directory1)
    os.removedirs(directory1)

    clear_directory(directory2)
    os.removedirs(directory2)


def natural_sort(elements: List[str]) -> List[str]:
    def natural_key(text: str):
        key = [int(chunk) if chunk.isdigit() else chunk.lower() for chunk in re.split('([0-9]+)', text)]
        print(f"Sorting key for '{text}': {key}")  # Debugging line
        return key

    return sorted(elements, key=natural_key)

def merger_pdf(pdf_files, output_folder):
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    with open(output_folder+"/merger_output.pdf", "wb") as output_pdf:
        merger.write(output_pdf)

    merger.close()

def convert_file_to_pdf(input_file, rename, output_folder):
    pythoncom.CoInitialize()

    try:
        # Get the absolute file path
        abs_input_file = os.path.abspath(input_file)
        abs_output_folder = os.path.abspath(output_folder)

        # Debugging:
        print(f"Input file: {abs_input_file}")
        print(f"Rename: {rename}")
        print(f"Output folder: {abs_output_folder}")

        # Get the base name and extension
        base_name = os.path.splitext(os.path.basename(abs_input_file))[0]
        ext = os.path.splitext(abs_input_file)[1].lower()

        # Debugging:
        print(f"Base name: {base_name}")
        print(f"Extension: {ext}")

        if ext in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pps']:
            print("Performing Office file conversion...")

            # Convert Office files to PDF (handling for Word, Excel, PowerPoint is the same as before)
            if ext in ['.doc', '.docx']:
                word_app = comtypes.client.CreateObject("Word.Application")
                word_app.Visible = False
                doc = word_app.Documents.Open(abs_input_file)
                pdf_output_path = os.path.join(abs_output_folder, f"{base_name}.pdf")
                doc.SaveAs(pdf_output_path, FileFormat=17)
                doc.Close(SaveChanges=False)
                word_app.Quit()

            elif ext in ['.xls', '.xlsx']:
                excel_app = comtypes.client.CreateObject("Excel.Application")
                excel_app.Visible = False
                wb = excel_app.Workbooks.Open(abs_input_file)
                pdf_output_path = os.path.join(abs_output_folder, f"{base_name}.pdf")
                wb.ExportAsFixedFormat(0, pdf_output_path)
                wb.Close(SaveChanges=False)
                excel_app.Quit()

            elif ext in ['.ppt', '.pptx', '.pps']:
                power_point_app = comtypes.client.CreateObject("PowerPoint.Application")
                presentation = power_point_app.Presentations.Open(abs_input_file, WithWindow=False)
                pdf_output_path = os.path.join(abs_output_folder, f"{base_name}.pdf")
                presentation.SaveAs(pdf_output_path, FileFormat=32)
                presentation.Close()
                power_point_app.Quit()

        elif ext in ['.jpeg', '.jpg', '.png', '.bmp']:
            print("Performing image conversion...")

            # Convert images to PDF
            image = Image.open(abs_input_file)
            image = image.convert('RGB')  # Convert image to RGB

            if rename.lower().endswith('.jpeg'):
                new_pdf_name = rename[:-5] + ".pdf"
            elif rename.lower().endswith(('.jpg', '.png', '.bmp')):
                new_pdf_name = rename[:-4] + ".pdf"

            pdf_output_path = os.path.join(abs_output_folder, new_pdf_name)

            # Create a PDF using ReportLab
            c = canvas.Canvas(pdf_output_path)
            img_width, img_height = image.size
            c.setPageSize((img_width, img_height))
            c.drawImage(abs_input_file, 0, 0, width=img_width, height=img_height)
            c.save()

        elif ext == '.gif':
            print("Performing GIF conversion...")

            image = Image.open(abs_input_file)
            pdf_output_path = os.path.join(abs_output_folder, f"{base_name}.pdf")
            c = canvas.Canvas(pdf_output_path)

            # Check if it's an animated GIF
            if getattr(image, "n_frames", 1) > 1:
                for frame in range(image.n_frames):
                    image.seek(frame)
                    image_frame = image.convert('RGB')

                    # Save the current frame to a temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                        temp_path = temp_file.name
                        image_frame.save(temp_path)

                    img_width, img_height = image_frame.size
                    c.setPageSize((img_width, img_height))
                    c.drawImage(temp_path, 0, 0, width=img_width, height=img_height)
                    c.showPage()  # Add a new page for each frame

                    # Clean up the temporary file
                    os.remove(temp_path)
            else:
                # Static GIF (or non-animated GIF)
                image = image.convert('RGB')
                img_width, img_height = image.size
                c.setPageSize((img_width, img_height))
                c.drawImage(abs_input_file, 0, 0, width=img_width, height=img_height)

            c.save()

        else:
            raise ValueError(
                "Unsupported file format. Supported formats: .doc, .docx, .xls, .xlsx, .ppt, .pptx, .pps, .jpeg, .jpg, .png, .bmp, .gif")

        # Handle renaming
        if rename.lower().endswith(('.docx', '.xlsx', '.pptx', '.jpeg')):
            new_name = rename[:-5] + ".pdf"
        elif rename.lower().endswith(('.doc', '.xls', '.ppt', '.pps', '.jpg', '.png', '.bmp', '.gif')):
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



def convert_pdf_to_word(input_file, output_format, output_folder):
    try:
        # Initialize COM objects
        pythoncom.CoInitialize()

        # Get the absolute file path
        abs_input_file = os.path.abspath(input_file)
        abs_output_folder = os.path.abspath(output_folder)
        base_name = os.path.splitext(os.path.basename(abs_input_file))[0]

        # Path to your Poppler binaries (adjust this to where you installed Poppler)
        poppler_path = r'C:\path\to\poppler\bin'  # Replace with the correct path to your Poppler bin folder

        if output_format.lower() in ['.doc', '.docx']:
            print("Converting PDF to Word...")
            output_file = os.path.join(abs_output_folder, f"{base_name}.docx")
            cv = Converter(abs_input_file)
            cv.convert(output_file)  # Converts PDF to .docx
            cv.close()

        else:
            raise ValueError("Unsupported output format. Supported formats: .docx, .pptx, .jpeg, .jpg, .png, .bmp")

        print(f"Converted PDF to {output_format} successfully!")

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
    session["points_dynamic"] = list[5]
    return (session["fn_dynamic"],
            session["ln_dynamic"],
            session["un_dynamic"],
            session["email_dynamic"],
            session["pw_dynamic"],
            session["points_dynamic"])

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
        if user_data["email"] == row[1] or user_data["username"] == row[0]:
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


def repeat_password(password, re_password):
    if password==re_password:
        return True
    else:
        return False









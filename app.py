from flask import Flask, request, redirect, url_for, send_from_directory, render_template
import os
import csv
from werkzeug.utils import secure_filename
from merge import merger_pdf

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MERGED_FOLDER'] = 'merged'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Ensure upload and merged folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['MERGED_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/profile", methods=["GET", "POST"])
def profile_page():
    return render_template("profile.html")

@app.route("/login", methods=["GET", "POST"])
def login_page():
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if request.method == 'POST':
        # Collect user data from the form
        user_data = {
            "first_name": request.form.get("signup_fn"),
            "last_name": request.form.get("signup_ln"),
            "username": request.form.get("signup_un"),
            "email": request.form.get("signup_email"),
            "password": request.form.get("signup_password"),
        }

        # Define the path to the CSV file
        csv_file_path = 'admin.csv'

        # Write user_data to CSV file
        file_exists = os.path.isfile(csv_file_path)
        with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=user_data.keys())
            # Write header if file is empty
            if not file_exists:
                writer.writeheader()
            # Write user data
            writer.writerow(user_data)

        return redirect(url_for('index'))

    return render_template("signup.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    files = request.files.getlist('file')

    if not files:
        return redirect(request.url)

    merged_filename = request.form.get("merged_filename")
    if not merged_filename:
        return redirect(request.url)

    merged_filename = secure_filename(merged_filename) + ".pdf"

    filenames = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            filenames.append(file_path)

    if filenames:
        merger_pdf(filenames)
        merged_file_path = os.path.join(app.config['MERGED_FOLDER'], merged_filename)
        os.rename(os.path.join(app.config['MERGED_FOLDER'], 'merger_output.pdf'), merged_file_path)
        return send_from_directory(app.config['MERGED_FOLDER'], merged_filename, as_attachment=True)
    else:
        return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, redirect, url_for, send_from_directory, render_template
import os
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

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    files = request.files.getlist('file')
    if not files:
        return redirect(request.url)

    filenames = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            filenames.append(file_path)

    if filenames:
        merger_pdf(filenames)
        merged_file_path = os.path.join(app.config['MERGED_FOLDER'], 'merger_output.pdf')
        return send_from_directory(app.config['MERGED_FOLDER'], 'merger_output.pdf', as_attachment=True)
    else:
        return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)

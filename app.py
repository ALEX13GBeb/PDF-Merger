from flask import Flask, request, redirect, url_for, send_from_directory, render_template
import os
from werkzeug.utils import secure_filename
from merge import merger_pdf

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MERGED_FOLDER'] = 'merged'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
# app.config['...'] is a key in Flask’s configuration object, app.config.
# It is being set to the string 'uploads/ merged'

# Ensure upload and merged folders exist,
# even if they have been deleted
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['MERGED_FOLDER'], exist_ok=True)

def allowed_file(filename): # Returns TRUE or FALSE
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS'] # Basically an AND Gate
# rsplit(".", 1) - splits the string into a LIST
# "." - specifies where to split
# 1 - specifies how many components the list should have = 2 (0 and 1)

@app.route('/') # This runs when someone visits the home page
def index(): # Basically the html call for the home page interface
    return render_template('index.html')

@app.route('/upload', methods=['POST']) # Decorator
# It tells the app that the following function should run if a Post request has been made
# to the \upload URL
# Post means sending data to the server (uploading files)

def upload_file():
    if 'file' not in request.files: # This means no files were uploaded
        return redirect(request.url)

    files = request.files.getlist('file') # Get a list of files uploaded
    # Allows the function to handle multiple files in one request

    if not files: # Checks if the files list is empty
        return redirect(request.url)

    filenames = []
    for file in files:
        if file and allowed_file(file.filename): # file.filename - This is an attribute of the FileStorage object (file) that gives the name of the uploaded file as a string.
            # In Flask, when you upload a file using a form,
            # each file is represented as a FileStorage object in request.files.
            # This object contains methods and attributes that provide information about the uploaded file.
            filename = secure_filename(file.filename) # Cleans up the Filename:
            # Removes Unsafe Characters
            # Avoids Path Traversals
            # Normalizes the Filename
            # Limits Length
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) # Creates the full path where the file will be saved
            file.save(file_path) # Saves the file to the specified path
            filenames.append(file_path)

    if filenames:
        merger_pdf(filenames)
        merged_file_path = os.path.join(app.config['MERGED_FOLDER'], 'merger_output.pdf')
        # Defines the path for the merged output pdf
        return send_from_directory(app.config['MERGED_FOLDER'], 'merger_output.pdf', as_attachment=True)
        # Sends the merged PDF file to the user as a downloadable attachment.
        # send_from_directory - ensures the file is sent from the specified directory.
    else:
        return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
    # Starts the app in debug mode
    # Debug Mode - let's you see errors and reloads the page automatically

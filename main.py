from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './accepted'  # Folder to save uploaded files
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the accepted folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return redirect(request.url)
    
    file = request.files['image']
    
    if file and allowed_file(file.filename):
        # Delete all files in the 'accepted' folder before saving the new one
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted existing file: {filename}")
        
        # Save the new file
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Print the filepath for debugging
        print(f"Saving file to {filepath}")
        
        file.save(filepath)

        # Check if the file exists after saving
        if os.path.exists(filepath):
            return f"File uploaded and saved successfully: {filename}"
        else:
            return "Error: File upload failed."
    else:
        return "File type not allowed."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

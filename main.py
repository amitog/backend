from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Import Flask-CORS
import os
import logging
import cloudinary
import cloudinary.uploader
app = Flask(__name__)

# Cloudinary configuration
cloudinary.config( 
    cloud_name = "dfx8ehu2t", 
    api_key = "227123151774292", 
    api_secret = "WV0sqJz3VIXVPV9sbAtfc-weEL0", # Click 'View API Keys' above to copy your API secret
    secure=True
)

# Enable CORS for all routes
CORS(app)

# Configurations for file upload
app.config['UPLOAD_FOLDER'] = './accepted'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the accepted folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

sensor_data = {
    "temperature": 0,
    "humidity": 0,
    "soil_moisture": 0
}

irrigation_state = False  # Track irrigation state (False = OFF, True = ON)

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Sensor data endpoint
@app.route('/sensor', methods=['POST'])
def sensor_data_update():
    global sensor_data
    try:
        data = request.json
        sensor_data["temperature"] = data.get("temperature")
        sensor_data["humidity"] = data.get("humidity")
        sensor_data["soil_moisture"] = data.get("soil_moisture")
        return jsonify({"status": "success", "message": "Sensor data received"}), 200
    except Exception as e:
        logging.error(f"Error updating sensor data: {e}")
        return jsonify({"status": "error", "message": "Invalid data"}), 400

# Endpoint to get sensor data
@app.route('/get_sensor_data', methods=['GET'])
def get_sensor_data():
    return jsonify(sensor_data), 200

# Endpoint to update irrigation state
@app.route('/irrigation_control', methods=['POST'])
def irrigation_control():
    global irrigation_state
    try:
        data = request.json
        irrigation_state = data.get("irrigation_on", False)
        print(f"Irrigation state updated: {'ON' if irrigation_state else 'OFF'}")
        return jsonify({
            "status": "success",
            "message": "Irrigation state updated",
            "irrigation_state": irrigation_state
        }), 200
    except Exception as e:
        logging.error(f"Error updating irrigation state: {e}")
        return jsonify({"status": "error", "message": "Invalid data"}), 400

# Endpoint to get irrigation state
@app.route('/get_irrigation_state', methods=['GET'])
def get_irrigation_state():
    return jsonify({"irrigation_state": irrigation_state}), 200

# File upload endpoint
@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    
    file = request.files['file']  # Ensure this matches the name in your HTML input field
    
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Upload to Cloudinary
            response = cloudinary.uploader.upload(file)
            # Return the Cloudinary URL
            return jsonify({
                "status": "success",
                "message": "File uploaded successfully",
                "url": response['url']
            }), 200
        except Exception as e:
            logging.error(f"Error uploading image: {e}")
            return jsonify({"status": "error", "message": "File upload failed"}), 500
    
    return jsonify({"status": "error", "message": "Invalid file type"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

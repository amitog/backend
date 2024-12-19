from flask import Flask, request, jsonify, redirect, render_template
from flask_cors import CORS  # Import Flask-CORS
import os
import logging

app = Flask(__name__)

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

irrigation_state = False  # Track irrigation state

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
        
        print(f"Temperature: {sensor_data['temperature']} °C")
        print(f"Humidity: {sensor_data['humidity']} %")
        print(f"Soil Moisture: {sensor_data['soil_moisture']}")
        
        return jsonify({"status": "success", "message": "Sensor data received"}), 200
    except Exception as e:
        logging.error(f"Error updating sensor data: {e}")
        return jsonify({"status": "error", "message": "Invalid data"}), 400

# Endpoint to get sensor data
@app.route('/get_sensor_data', methods=['GET'])
def get_sensor_data():
    return jsonify(sensor_data), 200

@app.route('/irrigation_control', methods=['POST'])
def irrigation_control():
    global irrigation_state
    try:
        data = request.json
        irrigation_state = data.get("irrigation_on", False)
        print(f"Irrigation state updated: {'ON' if irrigation_state else 'OFF'}")
        
        # Print the current irrigation state to the terminal
        print(f"Current Irrigation State: {'ON' if irrigation_state else 'OFF'}")
        
        return jsonify({
            "status": "success",
            "message": "Irrigation state updated",
            "irrigation_state": irrigation_state
        }), 200
    except Exception as e:
        logging.error(f"Error updating irrigation state: {e}")
        return jsonify({"status": "error", "message": "Invalid data"}), 400


@app.route('/get_irrigation_state', methods=['GET'])
def get_irrigation_state():
    return jsonify({"irrigation_state": "ON" if irrigation_state else "OFF"}), 200


# Image upload endpoint
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return redirect(request.url)
    
    file = request.files['image']
    
    if file and allowed_file(file.filename):
        # Optionally delete existing files, but consider if multiple uploads are needed
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted existing file: {filename}")
        
        # Save the new file
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Saving file to {filepath}")
        
        file.save(filepath)

        if os.path.exists(filepath):
            return redirect("https://frontend-five-gamma-91.vercel.app/")  # Redirect to your frontend URL
        else:
            return jsonify({"status": "error", "message": "File upload failed."}), 500
    else:
        return jsonify({"status": "error", "message": "File type not allowed."}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

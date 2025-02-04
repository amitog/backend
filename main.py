from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import logging
import cloudinary
import cloudinary.uploader
import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

# Cloudinary configuration
cloudinary.config(
    cloud_name="dfx8ehu2t",
    api_key="227123151774292",
    api_secret="WV0sqJz3VIXVPV9sbAtfc-weEL0",
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

# Load the saved model and label encoder
with open("fertilizer_model (1).pkl", "rb") as f:
    rf_classifier = pickle.load(f)

with open("label_encoder (1).pkl", "rb") as f:
    label_encoder = pickle.load(f)

# Load trained columns for ensuring matching columns
trained_columns = pd.read_pickle("trained_columns.pkl")

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Sensor data
sensor_data = {
    "temperature": 0,
    "humidity": 0,
    "soil_moisture": 0
}

irrigation_state = False  # Track irrigation state (False = OFF, True = ON)

# Function to scale and predict
def predict_fertilizer(sensor_data):
    # Prepare the input data
    input_data = {
        "Temparature": [sensor_data["temperature"]],
        "Humidity": [sensor_data["humidity"]],
        "Moisture": [sensor_data["soil_moisture"]],
        "Nitrogen": [20],  # Use a constant or fetch actual data
        "Potassium": [5],  # Use a constant or fetch actual data
        "Phosphorous": [15],  # Use a constant or fetch actual data
        "Soil Type": ["Loamy"],  # Use a constant or fetch actual data
        "Crop Type": ["Maize"]  # Use a constant or fetch actual data
    }

    # Convert input data to DataFrame
    input_df = pd.DataFrame(input_data)

    # One-Hot Encoding for categorical features (Soil Type and Crop Type)
    X_encoded_input = pd.get_dummies(input_df, columns=["Soil Type", "Crop Type"])

    # Ensure the columns of the input data match the trained model's columns
    missing_cols = set(trained_columns) - set(X_encoded_input.columns)

    # Add missing columns to match training columns, with all zero values
    for col in missing_cols:
        X_encoded_input[col] = 0

    # Reorder the columns to match the trained columns
    X_encoded_input = X_encoded_input[trained_columns]

    # Scale the numerical columns
    numerical_columns = ["Temparature", "Moisture", "Nitrogen", "Potassium", "Phosphorous"]
    scaler = StandardScaler()

    # Scale the numerical columns
    X_encoded_input[numerical_columns] = scaler.fit_transform(X_encoded_input[numerical_columns])

    # Predict using the trained model
    prediction = rf_classifier.predict(X_encoded_input)

    # Decode the prediction to the original label
    predicted_fertilizer = label_encoder.inverse_transform(prediction)

    return predicted_fertilizer[0]

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

# Prediction endpoint
@app.route('/prediction', methods=['GET'])
def prediction():
    try:
        predicted_fertilizer = predict_fertilizer(sensor_data)
        return jsonify({
            "status": "success",
            "predicted_fertilizer": predicted_fertilizer
        }), 200
    except Exception as e:
        logging.error(f"Error generating prediction: {e}")
        return jsonify({"status": "error", "message": "Prediction failed"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

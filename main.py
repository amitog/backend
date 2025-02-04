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
with open("fertilizer_model.pkl", "rb") as f:
    rf_classifier = pickle.load(f)

with open("label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

# Load trained columns for ensuring matching columns
trained_columns = pd.read_pickle("trained_columns.pkl")

# Sensor data
sensor_data = {
    "temperature": 0,
    "humidity": 0,
    "soil_moisture": 0
}

irrigation_state = False  # Track irrigation state (False = OFF, True = ON)

# Function to scale and predict
def predict_fertilizer(data):
    # Prepare the input data
    input_data = {
        "Temparature": [data["temperature"]],
        "Humidity": [data["humidity"]],
        "Moisture": [data["soil_moisture"]],
        "Nitrogen": [data["nitrogen"]],
        "Potassium": [data["potassium"]],
        "Phosphorous": [data["phosphorous"]],
        "Soil Type": [data["soilType"]],
        "Crop Type": [data["cropType"]]
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

# Sensor data update endpoint
@app.route('/sensor', methods=['POST'])
def sensor_data_update():
    global sensor_data
    try:
        data = request.json
        sensor_data.update(data)
        return jsonify({"status": "success", "message": "Sensor data received"}), 200
    except Exception as e:
        logging.error(f"Error updating sensor data: {e}")
        return jsonify({"status": "error", "message": "Invalid data"}), 400

# Get sensor data endpoint
@app.route('/get_sensor_data', methods=['GET'])
def get_sensor_data():
    return jsonify(sensor_data), 200

# Prediction endpoint (now accepting POST requests)
@app.route('/prediction', methods=['POST'])
def prediction():
    try:
        data = request.json  # Get JSON input from frontend
        predicted_fertilizer = predict_fertilizer(data)  # Predict using received data
        return jsonify({
            "status": "success",
            "prediction": predicted_fertilizer
        }), 200
    except Exception as e:
        logging.error(f"Error generating prediction: {e}")
        return jsonify({"status": "error", "message": "Prediction failed"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

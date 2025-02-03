<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Input Form</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f7f9fc;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            color: #333;
        }

        .card-item {
            background-color: #fff;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border-radius: 12px;
            padding: 30px;
            width: 320px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .card-item:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 45px rgba(0, 0, 0, 0.15);
        }

        h2 {
            text-align: center;
            color: #333;
            font-size: 26px;
            margin-bottom: 20px;
        }

        label {
            font-size: 14px;
            color: #555;
            margin-bottom: 8px;
            display: block;
            font-weight: 500;
        }

        input[type="number"],
        select {
            width: 100%;
            padding: 12px 15px;
            margin-bottom: 18px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 15px;
            transition: border-color 0.3s ease;
            background-color: #f9f9f9;
        }

        input[type="number"]:focus,
        select:focus {
            border-color: #007bff;
            outline: none;
            background-color: #fff;
        }

        input[type="submit"] {
            background-color: #007bff;
            color: white;
            padding: 14px 20px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            transition: background-color 0.3s ease, transform 0.3s ease;
        }

        input[type="submit"]:hover {
            background-color: #0056b3;
            transform: translateY(-3px);
        }

        input[type="submit"]:active {
            transform: translateY(0);
        }

        .form-group {
            margin-bottom: 20px;
        }

        .card-item a {
            text-decoration: none;
        }

        /* Mobile responsiveness */
        @media (max-width: 480px) {
            .card-item {
                width: 90%;
                padding: 20px;
            }

            h2 {
                font-size: 22px;
            }

            input[type="submit"] {
                font-size: 14px;
            }
        }

        /* Custom Styles for Real-time Data Display */
        #realTimeData {
            margin-top: 20px;
            font-size: 16px;
            color: #333;
        }

        .gauge-container {
            display: flex;
            justify-content: space-between;
            margin-top: 10px;
        }

        .gauge {
            text-align: center;
        }

        /* Loading Indicator Style */
        #loading {
            display: none;
            text-align: center;
            font-size: 16px;
            color: #007bff;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <a href="#" class="card-item">
        <h2>Input Data</h2>
        <div id="realTimeData">
            <h3>Real-Time Data</h3>
            <div class="gauge-container">
                <div class="gauge">
                    <h4>Temperature</h4>
                    <p id="tempDisplay">30°C</p>
                </div>
                <div class="gauge">
                    <h4>Humidity</h4>
                    <p id="humidityDisplay">60%</p>
                </div>
                <div class="gauge">
                    <h4>Moisture</h4>
                    <p id="moistureDisplay">45%</p>
                </div>
            </div>
        </div>
        <form id="inputForm">
            <div class="form-group">
                <label for="nitrogen">Nitrogen (%):</label>
                <input type="number" id="nitrogen" name="nitrogen" value="20">
            </div>

            <div class="form-group">
                <label for="potassium">Potassium (%):</label>
                <input type="number" id="potassium" name="potassium" value="5">
            </div>

            <div class="form-group">
                <label for="phosphorous">Phosphorous (%):</label>
                <input type="number" id="phosphorous" name="phosphorous" value="15">
            </div>

            <div class="form-group">
                <label for="soilType">Soil Type:</label>
                <select id="soilType" name="soilType">
                    <option value="Loamy" selected>Loamy</option>
                    <option value="Sandy">Sandy</option>
                    <option value="Clayey">Clayey</option>
                    <option value="Black">Black</option>
                    <option value="Red">Red</option>
                </select>
            </div>

            <div class="form-group">
                <label for="cropType">Crop Type:</label>
                <select id="cropType" name="cropType">
                    <option value="Sugarcane" selected>Sugarcane</option>
                    <option value="Cotton">Cotton</option>
                    <option value="Millets">Millets</option>
                    <option value="Paddy">Paddy</option>
                    <option value="Pulses">Pulses</option>
                </select>
            </div>

            <input type="submit" value="Submit">
        </form>

        <!-- Loading Indicator -->
        <div id="loading">Please wait, processing your data...</div>

        <!-- Prediction Result -->
        <div id="predictionResult"></div>
    </a>

    <script>
        // Function to fetch real-time data from the backend
        async function fetchSensorData() {
            try {
                const response = await fetch('https://backend-4ml0.onrender.com/get_sensor_data');
                if (response.ok) {
                    const data = await response.json();
                    updateRealTimeData(data);
                } else {
                    console.error('Failed to fetch sensor data');
                }
            } catch (error) {
                console.error('Error fetching sensor data:', error);
            }
        }

        // Update the real-time data display on the page
        function updateRealTimeData(data) {
            document.getElementById('tempDisplay').innerText = `${data.temperature}°C`;
            document.getElementById('humidityDisplay').innerText = `${data.humidity}%`;
            document.getElementById('moistureDisplay').innerText = `${data.soil_moisture}%`;
        }

        // Function to send input data to /prediction and display the result
        async function submitForm(event) {
            event.preventDefault();
            // Show the loading indicator
            document.getElementById('loading').style.display = 'block';

            // Get input values
            const nitrogen = document.getElementById('nitrogen').value;
            const potassium = document.getElementById('potassium').value;
            const phosphorous = document.getElementById('phosphorous').value;
            const soilType = document.getElementById('soilType').value;
            const cropType = document.getElementById('cropType').value;

            // Prepare the payload for prediction
            const data = {
                nitrogen: nitrogen,
                potassium: potassium,
                phosphorous: phosphorous,
                soilType: soilType,
                cropType: cropType
            };

            try {
                const response = await fetch('https://backend-4ml0.onrender.com/prediction', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                // Hide loading and show the prediction result
                document.getElementById('loading').style.display = 'none';
                document.getElementById('predictionResult').innerText = `Predicted Fertilizer: ${result.prediction}`;
            } catch (error) {
                console.error('Error submitting data for prediction:', error);
                document.getElementById('loading').style.display = 'none';
                document.getElementById('predictionResult').innerText = 'An error occurred. Please try again.';
            }
        }

        // Fetch data on page load and every 5 seconds
        window.onload = function () {
            fetchSensorData();
            setInterval(fetchSensorData, 5000);

            // Attach the submit event handler
            document.getElementById('inputForm').addEventListener('submit', submitForm);
        };
    </script>
</body>
</html>

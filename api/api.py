import re
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import dbhandler as dbHandler
import pickle
import secrets
import xgboost as xgb
import pandas as pd
import numpy as np
import logging
import io

api = Flask(__name__)
cors = CORS(api)
api.config["CORS_HEADERS"] = "Content-Type"
api.config["SECRET_KEY"] = secrets.token_hex(16)

limiter = Limiter(
    get_remote_address,
    app=api,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)


def check_api_key():
    # Check if the request has an Authorization header with a valid API key.
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        api_key = auth_header.split(" ")[1]
        if dbHandler.is_valid_api_key(api_key):
            return None
    return jsonify({"error": "Invalid API key"}), 401


@api.route("/get_prediction", methods = ["GET"])
@limiter.limit("1/second", override_defaults=False)
def get_prediction():
    api_key_error = check_api_key()
    if api_key_error:
        return api_key_error
    
    # Check if all required features are present in the request and are of numerical type.
    features = ['cement', 'blast_furnace_slag', 'fly_ash', 'water', 'superplasticizer', 'coarse_aggregate', 'fine_aggregate', 'age']
    for feature in features:
        if feature not in request.args:
            return jsonify({'error': f'Missing feature: {feature}'}), 400
        try:
            float(request.args[feature])
        except ValueError:
            return jsonify({'error': f'Invalid value for feature: {feature}. Need numerical type.'}), 400
    
    # Convert request arguments to pd.DataFrame and engineer features
    data_dict = {feature: [(request.args.get(feature, type = float))] for feature in features}
    data = pd.DataFrame.from_dict(data_dict)
    data['cement_to_water_ratio'] = data['cement'] / data['water']
    data['fine_aggregate_to_water_ratio'] = data['fine_aggregate'] / data['water']
    data['coarse_aggregate_to_water_ratio'] = data['coarse_aggregate'] / data['water']
    data.replace([np.inf, -np.inf], 0, inplace=True)

    features_engineered = ['cement_to_water_ratio', 'fine_aggregate_to_water_ratio', 'coarse_aggregate_to_water_ratio']
    features.extend(features_engineered)

    # Load the fitted scaler and model.
    scaler = pickle.load(open('C:/Users/admin/Documents/GitHub/2025SE-Mike.N-HSC-AT2/model/scaler.pkl', 'rb'))
    data = scaler.transform(data)
    data = pd.DataFrame(data, columns=features)

    data = xgb.DMatrix(data)
    model = pickle.load(open('C:/Users/admin/Documents/GitHub/2025SE-Mike.N-HSC-AT2/model/xgboost.pkl', 'rb'))
    prediction = model.predict(data)
    return jsonify({"prediction": prediction.tolist()}), 201


@api.route("/get_api_key", methods=["POST"])
@limiter.limit("1/second", override_defaults=False)
def get_api_key():
    # Extract user information from the request with an email
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "User information is required"}), 400
    
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        return jsonify({"error": "Invalid email format"}), 400

    # Generate a new API key
    new_api_key = secrets.token_hex(32)

    # Store the API key in the database
    response = dbHandler.insert_user(email, new_api_key)
    if response[1]:
        return jsonify({"api_key": new_api_key}), 201
    else:
        return jsonify({"error": response[0]}), 400
    

@api.route("/upload_csv", methods=["POST"])
@limiter.limit("5/minute", override_defaults=False)
def upload_csv():
    # Check API key validity
    api_key_error = check_api_key()
    if api_key_error:
        return api_key_error

    # Check if a file is included in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    # Check if the file has a valid name
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Check if the file is a CSV
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Invalid file format. Only .csv files are allowed"}), 400

    try:
        # Read the CSV file into a pandas DataFrame
        stream = io.StringIO(file.stream.read().decode("UTF-8"))
        data = pd.read_csv(stream)

        # Validate each row in the DataFrame
        for _, row in data.iterrows():
            record = row.to_dict()
            if not dbHandler.validate_json(record, 'upload'):
                return jsonify({"error": "One or more records in the CSV are invalid."}), 400

        # Process the valid data
        data.to_csv('../data/uploaded_data.csv', index=False)
        return jsonify({"message": "CSV data uploaded successfully."}), 201

    except Exception as e:
        return jsonify({"error": "Failed to process the CSV file.", "details": str(e)}), 500

if __name__ == "__main__":
    api.run(debug=True, host="0.0.0.0", port=3000)
    logging.basicConfig(level=logging.DEBUG)
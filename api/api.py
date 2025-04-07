from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import dbhandler as dbHandler
import pickle
import secrets

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
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        api_key = auth_header.split(" ")[1]
        if dbHandler.is_valid_api_key(api_key):
            return None
    return jsonify({"error": "Invalid API key"}), 401

@api.route("/get_prediction", methods = ["GET"])
@limiter.limit("1/second", overide_defaults=False)
def get_prediction():
    api_key_error = check_api_key()
    if api_key_error:
        return api_key_error
    
    features = ['cement', 'blast_furnace_slag', 'fly_ash', 'water', 'superplasticizer', 'coarse_aggregate', 'fine_aggregate', 'age']
    for feature in features:
        if feature not in request.args:
            return jsonify({'error': f'Missing feature: {feature}'}), 400
        try:
            request.args[feature] = float(request.args[feature])
        except ValueError:
            return jsonify({'error': f'Invalid value for feature: {feature}. Need numerical type.'}), 400
    
    model = pickle.load(open('model/xgboost.sav', 'rb'))
    return model.predict([[request.args[feature] for feature in features]])

if __name__ == "__main__":
    api.run(debug=True, host="0.0.0.0", port=3000)
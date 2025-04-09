from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import os
from flask_wtf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, FloatField
from wtforms.validators import DataRequired, Email, Length, Optional
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import secrets
import dbhandler as dbHandler
from flask_cors import CORS
import requests
import time
import re
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField


app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"
app.config["SECRET_KEY"] = secrets.token_hex(16)
app_log = logging.getLogger(__name__)
logging.basicConfig(
    filename="security_log.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

@app.after_request
def apply_csp(response):
    response.headers['Content-Security-Policy'] = (
        "base-uri 'self' https://github.dev; "
        "default-src 'self' https://github.dev;"
        "style-src https://github.dev https://cdn.jsdelivr.net 'self' ;"
        "script-src https://cdn.jsdelivr.net 'self';"
        "style-src-elem https://cdn.jsdelivr.net 'self';"
        "script-src-elem https://cdn.jsdelivr.net 'self';"
        "img-src 'self' data:; "
        "media-src 'self'; "
        "font-src 'self'; "
        "object-src 'self'; "
        "child-src 'self'; "
        "connect-src 'self'; "
        "worker-src 'self'; "
        "report-uri /csp_report; "
        "frame-ancestors 'none'; "
        "form-action 'self'; "
        "frame-src 'none';"
        "manifest-src 'self' https://github.dev;"
        )
    return response

class DataEntryForm(FlaskForm):
    api_key = StringField('API Key', validators=[DataRequired()])
    cement = FloatField('Cement (kg in a m3 mixture)', validators=[DataRequired()])
    blast_furnace_slag = FloatField('Blast Furnace Slag (kg in a m3 mixture)', validators=[DataRequired()])
    fly_ash = FloatField('Fly Ash (kg in a m3 mixture)', validators=[DataRequired()])
    water = FloatField('Water (kg in a m3 mixture)', validators=[DataRequired()])
    superplasticizer = FloatField('Superplasticizer (kg in a m3 mixture)', validators=[DataRequired()])
    coarse_aggregate = FloatField('Coarse Aggregate (kg in a m3 mixture)', validators=[DataRequired()])
    fine_aggregate = FloatField('Fine Aggregate (kg in a m3 mixture)', validators=[DataRequired()])
    age = FloatField('Age (days)', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/prediction", methods=["GET", "POST"])
def prediction():
    form = DataEntryForm()
    if form.validate_on_submit():
        # Process the form data and make a prediction
        data = {
            'api_key': form.api_key.data,
            'cement': form.cement.data,
            'blast_furnace_slag': form.blast_furnace_slag.data,
            'fly_ash': form.fly_ash.data,
            'water': form.water.data,
            'superplasticizer': form.superplasticizer.data,
            'coarse_aggregate': form.coarse_aggregate.data,
            'fine_aggregate': form.fine_aggregate.data,
            'age': form.age.data
        }
        # Check if the API key is valid
        api_key = form.api_key.data
        if not api_key:
            return jsonify({"error": "API key is required"}), 401
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        try:
            response = requests.get('http://localhost:3000/get_prediction', params=data, headers=headers)
            if response.status_code == 201:
                prediction = response.json().get("prediction", "No prediction available")
                flash(f"Prediction: {prediction}", "success")
            else:
                error_message = response.json().get("error", "An error occurred")
                flash(error_message, "danger")
        except requests.exceptions.RequestException as e:
            flash(f"Error connecting to the prediction API: {str(e)}", "danger")

    return render_template("prediction.html", form=form)

@limiter.limit("1/second", override_defaults=False)
@app.route("/get_api_key", methods=["GET", "POST"])
def get_api_key_page():
    if request.method == "POST":
        email = request.json.get("email")
        if not email:
            return jsonify({"error": "Email is required"}), 400

        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            return jsonify({"error": "Invalid email format"}), 400

        new_api_key = secrets.token_hex(32)
        response = dbHandler.insert_user(email, new_api_key)
        if response[1]:
            return jsonify({"api_key": new_api_key}), 201
        else:
            return jsonify({"error": response[0]}), 400
    return render_template("get_api_key.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
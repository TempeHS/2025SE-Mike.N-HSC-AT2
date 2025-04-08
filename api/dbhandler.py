import sqlite3 as sql
from jsonschema import validate
from datetime import datetime

def insert_user(email, api_key):
    try:
        con = sql.connect("C:/Users/admin/Documents/GitHub/2025SE-Mike.N-HSC-AT2/.databaseFiles/users.db")
        cur = con.cursor()
        cur.execute("INSERT INTO users (K3hq4_email, UsA17_api_key) VALUES (?, ?)", (email, api_key))
        con.commit()
        con.close()
    except sql.IntegrityError:
        return ('User already exists', False)
    return ('User added successfully', True)

def is_valid_api_key(value):
    con = sql.connect("C:/Users/admin/Documents/GitHub/2025SE-Mike.N-HSC-AT2/.databaseFiles/users.db")
    cur = con.cursor()
    column_name = 'UsA17_api_key'
    query = f'SELECT * FROM users WHERE {column_name} = ?'
    user = cur.execute(query, (value,)).fetchone()
    con.close()
    if user:
        return True
    else: 
        return False
    
schema = {
    "type": "object",
    "properties": {
        "cement": {"type": "number"},
        "water": {"type": "number"},
        "fine_aggregate": {"type": "number"},
        "coarse_aggregate": {"type": "number"},
        "fly_ash": {"type": "number"},
        "superplasticizer": {"type": "number"},
        "blast_furnace_slag": {"type": "number"},
        "age": {"type": "number"}
    },
    "required": [
        "cement",
        "water",
        "fine_aggregate",
        "coarse_aggregate",
        "fly_ash",
        "superplasticizer",
        "blast_furnace_slag",
        "age"
    ]
}

schema_upload = {
    "type": "object",
    "properties": {
        "cement": {"type": "number"},
        "water": {"type": "number"},
        "fine_aggregate": {"type": "number"},
        "coarse_aggregate": {"type": "number"},
        "fly_ash": {"type": "number"},
        "superplasticizer": {"type": "number"},
        "blast_furnace_slag": {"type": "number"},
        "age": {"type": "number"},
        "strength": {"type": "number"}
    },
    "required": [
        "cement",
        "water",
        "fine_aggregate",
        "coarse_aggregate",
        "fly_ash",
        "superplasticizer",
        "blast_furnace_slag",
        "age",
        "strength"
    ]
}

def validate_json(json_data, type):
    try:
        if type == 'upload':
            validate(instance=json_data, schema=schema_upload)
        elif type == 'get_prediction':
            validate(instance=json_data, schema=schema)
        return True
    except:
        return False
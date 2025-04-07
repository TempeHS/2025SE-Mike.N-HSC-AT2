import sqlite3 as sql
from jsonschema import validate
from datetime import datetime

def insert_user(email, api_key):
    con = sql.connect(".databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO users (K3hq4_email, UsA17_api_key) VALUES (?, ?)", (email, api_key))
    con.commit()
    con.close()

def is_valid_api_key(value):
    con = sql.connect(".databaseFiles/database.db")
    cur = con.cursor()
    column_name = 'UsA17_api_key'
    query = f'SELECT * FROM users WHERE {column_name} = ?'
    user = cur.execute(query, (value,)).fetchone()
    con.close()
    if user:
        return True
    else: 
        return False
    
schema = {"type": "object",
    "validationLevel": "strict",
    "properties": {
        "cement":{
            "type": "number"
        },
        "water":{
            "type": "number"
        },
        "fine_aggregate":{
            "type": "number"
        },
        "course_aggregate":{
            "type": "number"
        },
        "fly_ash":{
            "type": "number"
        },
        "superplasticizer":{
            "type": "number"
        },
        "blast_furnace_slag":{
            "type": "number"
        }
    },
    "required": ["developer", "project", "start_time", "end_time", "repo_url", "dev_note", "code_snippet", "language", "owner"]
}

def validate_json(json_data):
    try:
        validate(instance=json_data, schema=schema)
        return True
    except:
        return False
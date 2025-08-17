from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg2, requests, bcrypt, jwt, datetime, os

app = Flask(__name__)
cors = CORS(app, methods="*")

load_dotenv()

private_key = ''

with open("private.pem") as f:
    private_key = f.read()

connection = psycopg2.connect(
    host="localhost",
    user="postgres",
    database="microservice-calc",
    password="root"
)

cur = connection.cursor()

# API end point to allow users to register and then immeditally login
@app.route("/register", methods=['POST'])
def register():

    try:

        data = request.get_json()

        username = data['username']
        email = data['email']
        password = data['password']

        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        row = cur.fetchall()

        salts = bcrypt.gensalt()

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salts).decode('utf-8')

        cur.execute(
            "INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s)", (username, email, hashed_password)
        )

        connection.commit()

        return jsonify({ "message": "Successfully registered"}), 201
    except Exception as e:
        print(f"ERROR: {e}")

        return jsonify({ "message": "error" }), 500

# API end point to allow users to login with email and password
# Postgres first checks to see if the email exists then checks to see if the password matches the one the user entered
# Passwords have to be checked using bcrypt's checkpw
@app.route("/login", methods=['POST'])
def login():

    try:
        data = request.get_json()

        email = data['email']
        password = data['password']

        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        rows = cur.fetchall()

        if len(rows) != 0:
            
            if bcrypt.checkpw(password.encode('utf-8'), rows[0][3].encode('utf-8')):

                payload = {
                    "userID": rows[0][0],
                    "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
                }

                token = jwt.encode(payload, private_key, algorithm="RS256")

                return jsonify({ "message": "successfull login", "token": token }), 200
            else:
                return jsonify({ "message": "incorrect password" }), 403
        
        else:
            return jsonify({ "message": "No user with this email exists" }), 404
            
    except Exception as e:
        print(f'ERROR: {e}')

        return jsonify({ "message": "error" }), 500
    
if __name__ == "__main__":
    app.run(debug=True, port=5002)

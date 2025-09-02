from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg2, requests, bcrypt, jwt, datetime, os

app = Flask(__name__)
cors = CORS(app, methods="*")

load_dotenv()

base_dir = os.path.dirname(__name__)
key_path = os.path.join(base_dir, "keys", "private_key.pem")

private_key = ''

with open(key_path, "r") as f:
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

        if len(row) == 0:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cur.execute(
                "INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s)", (username, email, hashed_password)
            )

            connection.commit()

            return jsonify({ "message": "Successfully registered", "action": "register" }), 201

        return jsonify({ "message": "This email already exists. Use a different email", "action": "register" }), 201
    except Exception as e:
        print(f"ERROR: {e}")

        return jsonify({ "message": "error", "action": "register" }), 500

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
        row = cur.fetchone()

        if row:
            
            if bcrypt.checkpw(password.encode('utf-8'), row[3].encode('utf-8')):

                payload = {
                    "userID": row[0],
                    "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
                }

                token = jwt.encode(payload, private_key, algorithm="RS256")

                return jsonify({ "message": "successfull login", "action": "login" ,"token": token }), 200
            else:
                return jsonify({ "message": "incorrect password", "action": "login" }), 403
        
        else:
            return jsonify({ "message": "No user with this email exists", "action": "login" }), 404
            
    except Exception as e:
        print(f'ERROR: {e}')

        return jsonify({ "message": "error", "action": "login" }), 500

# Making an api endpoint which logs the user out by deleting their cookie. My middleware for the application will make sure
# the user is the on the correct page depending on if they do or don't have a cookie
@app.route("/logout", methods=['POST'])
def logout():
    
    try:

        return jsonify({ "message": "Successfully logged out", "action": "logout" }), 200
    
    except Exception as e:
        print(f'ERROR: {e}')

        return jsonify({ "message": "error", "action": "logout" }), 500
    
if __name__ == "__main__":
    app.run(debug=True, port=5002)

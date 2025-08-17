from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import psycopg2, requests

app = Flask(__name__)
cors = CORS(app, methods="*")

connection = psycopg2.connect(
    host="localhost",
    user="postgres",
    database="microservice-calc",
    password="root"
)

cur = connection.cursor()

@app.route("/get_users")
def get_users():

    try:

        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        
        print(cur.description)

        key_names = [desc[0] for desc in cur.description]

        results = [dict(zip(key_names, row)) for row in rows]

        return jsonify(results)

    except Exception as e:
        print(f"ERROR:{e}")

if __name__ == "__main__":
    app.run(debug=True, port=5001)

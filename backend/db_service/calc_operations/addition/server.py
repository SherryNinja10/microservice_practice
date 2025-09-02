from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg2, requests, bcrypt, jwt, datetime, os

app = Flask(__name__)
cors = CORS(app, methods="*")

load_dotenv()

base_dir = os.path.dirname(__name__)
key_path = os.path.join(base_dir, "keys", "public_key.pem")

public_key = ''

with open(key_path, "r") as f:
    public_key = f.read()

connection = psycopg2.connect(
    host="localhost",
    user="postgres",
    database="microservice-calc",
    password="root"
)

cur = connection.cursor()

@app.route("/addition", methods=['POST'])
def addition():
    try:

        token = request.cookies.get('token')

        print(token)

        if token:

            print(token)

            payload = jwt.decode(token, public_key, algorithms=['RS256'])
            print(payload)

            # payload = jwt.decode(token, options={"verify_signature": False})
            # print("Decoded payload without verifying:", payload)

            user_id = payload["userID"]

            data = request.get_json()

            number1 = data["number1"]
            number2 = data['number2']

            answer = number1 + number2

            cur.execute(
                "INSERT INTO addition (number1, number2, answer, user_id) VALUES (%s, %s, %s, %s)", (number1, number2, answer, user_id)
            )

            connection.commit()

            return jsonify({ "answer": answer, "calculation": f"{number1} + {number2}", "message": "Addition calculation done and added to addition history" }), 200
        
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return jsonify({ "message": "error token has expired" }), 401

    except jwt.InvalidSignatureError:
        print("Invalid signature")
        return jsonify({ "message": "error invalid signature", "token": token }), 401

    except jwt.DecodeError:
        print("Decode error")
        return jsonify({ "message": "error decoding token", "token": token }), 401

    except jwt.InvalidAudienceError:
        print("Invalid audience")
        return jsonify({ "message": "error invalid audience", "token": token }), 401

    except jwt.InvalidIssuerError:
        print("Invalid issuer")
        return jsonify({ "message": "error invalid issuer", "token": token }), 401

    except jwt.InvalidIssuedAtError:
        print("Invalid issued at (iat)")
        return jsonify({ "message": "error invalid issued at", "token": token }), 401

    except jwt.ImmatureSignatureError:
        print("Token not valid yet (nbf)")
        return jsonify({ "message": "error token not valid yet", "token": token }), 401

    except jwt.InvalidTokenError:
        # catches all other token errors not covered above
        print("Invalid token")
        return jsonify({ "message": "error invalid token", "token": token }), 401
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({ "message": "error" }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5003)
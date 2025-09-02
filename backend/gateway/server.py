from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
cors = CORS(app, methods="*")

db_microservice = "http://127.0.0.1:5001"
auth_microservice = "http://127.0.0.1:5002"
addition_microservice = "http://127.0.0.1:5003"

@app.route("/db/<path:path>", methods=['GET', 'POST', 'PUT', 'DELETE'])
def database_function(path):
    url = f"{db_microservice}/{path}"

    resp = requests.request(
        method=request.method,
        url=url,
        headers={key: value for key, value in request.headers if key != 'HOST'},
        data=request.get_data(),
        params=request.args
    )

    return Response(resp.content, status=resp.status_code, headers=dict(resp.headers))

@app.route("/auth/<path:path>", methods=['GET', 'POST', 'PUT', 'DELETE'])
def auth_function(path):
    url = f"{auth_microservice}/{path}"

    resp = requests.request(
        method=request.method,
        url=url,
        headers={key: value for key, value in request.headers if key != 'HOST'},
        data=request.get_data(),
        params=request.args,
        cookies=request.cookies
    )

    res = Response(resp.content, status=resp.status_code, headers=dict(resp.headers))

    if resp.json().get("token"):
        res.set_cookie("token", value=resp.json()["token"], httponly=True, secure=False)

    if resp.json().get("action") == "logout":
        res.delete_cookie("token")

    return res

@app.route("/addition/<path:path>", methods=['GET', 'POST', 'PUT', 'DELETE'])
def addition_function(path):
    url = f"{addition_microservice}/{path}"

    resp = requests.request(
        url=url,
        method=request.method,
        headers={key: value for key, value in request.headers if key != 'HOST'},
        data=request.get_data(),
        params=request.args,
        cookies=request.cookies
    )

    return Response(resp.content, status=resp.status_code, headers=dict(resp.headers)) 

if __name__ == '__main__':
    app.run(debug=True,port=5000)
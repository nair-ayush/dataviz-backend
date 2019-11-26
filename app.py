import boto3
import jwt
import logging
from datetime import datetime, timedelta
from flask_cors import CORS
from flask import Flask, jsonify, request, abort

from helpers import encode_auth_token, decode_auth_token, uploadToS3

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})

@app.route('/')
def hello(methods=["GET"]):
    return jsonify("dataviz / endpoint")


@app.route('/signin', methods=['POST'])
def login():
    if not request.json or 'username' not in request.json.keys() or 'password' not in request.json.keys():
        return jsonify("Incorrect form submission"), 400
    token = encode_auth_token(request.json["username"])
    return jsonify({"username": request.json["username"], 'token': token.decode('utf-8')}), 200


@app.route('/register', methods=['POST'])
def register():
    if not request.json or 'email' not in request.json.keys() or 'username' not in request.json.keys():
        return jsonify("Incorrect form submission"), 400

    return jsonify({'success': True, 'userId': request.json["username"]}), 200


@app.route('/uploadFile', methods=['POST'])
def upload():
    if not request.json or 'filePath' not in request.json.keys():
        return jsonify("Incorrect form submission"), 400
    try:
        token = request.headers['Authorization']
        print(token)
    except KeyError:
        abort(401)

    payload = decode_auth_token(token)
    # print(payload)
    file_path = request.json['filePath']
    if 'bucketName' in request.json.keys():
        bucket_name = request.json['bucketName']
        if uploadToS3(file_path, payload):
            return jsonify({"status": "OK"}), 200
        else:
            return jsonify({"status": "FAIL"}), 400
    else:
        if uploadToS3(file_path, payload):
            return jsonify({"status": "OK"}), 200
        else:
            return jsonify({"status": "FAIL"}), 400

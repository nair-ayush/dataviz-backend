import boto3
import jwt
import logging
import pandas as pd
from datetime import datetime, timedelta
from src.statistics import summary
from flask_cors import CORS
from flask import Flask, jsonify, request, abort

from helpers import encode_auth_token, decode_auth_token, uploadToS3, downloadFromS3

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
    if uploadToS3(file_path, payload):
        df = pd.read_csv(file_path)
        return jsonify({"status": "OK", "fileName": file_path, "data": df.to_dict(orient='records')}), 200
    else:
        return jsonify({"status": "FAIL"}), 400


@app.route('/downloadTable/<string:project_id>', methods=["POST"])
def downloadProject(project_id, token=None):
    try:
        if token is None:
            token = request.headers['Authorization']
    except KeyError:
        abort(401)

    payload = decode_auth_token(token)
    if downloadFromS3(payload+project_id):
        return jsonify("OK")


@app.route('/table/summary/<string:project_id>', methods=['GET'])
def getTableSummary(project_id):
    try:
        token = request.headers['Authorization']
    except KeyError:
        abort(401)
    payload = decode_auth_token(token)
    object_name = payload+"/"+project_id
    print(object_name)
    if downloadFromS3(object_name):
        df = pd.read_csv('./temp/'+project_id)
        return jsonify({"data": summary(df)}), 200
    else:
        return jsonify("FAIL"), 500


# @app.route('/table/dimensions/<string:project_id>', methods=['GET'])
# def getTableSummary(project_id):
#     try:
#         token = request.headers['Authorization']
#     except KeyError:
#         abort(401)
#     payload = decode_auth_token(token)
#     object_name = payload+"/"+project_id
#     # print(object_name)
#     if downloadFromS3(object_name):
#         df = pd.read_csv('./temp/'+project_id)
#         return jsonify({"data": summary(df)}), 200
#     else:
#         return jsonify("FAIL"), 500

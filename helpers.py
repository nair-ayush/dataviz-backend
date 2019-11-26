import jwt
import logging
import boto3
from secrets import SECRET_KEY
from datetime import datetime, timedelta
from secrets import BUCKET_NAME
from botocore.exceptions import ClientError


def uploadToS3(file_name, user_name, bucket=BUCKET_NAME):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    object_name = user_name + "/" + file_name.split("/")[-1]

    # Upload the file
    s3 = boto3.client('s3')
    # print("\n BUCKETS \n", s3_client.list_buckets())
    try:
        response = s3.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=10),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm='HS256'
        )
    except Exception as e:
        return e


def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(auth_token, SECRET_KEY)
        # print(payload)
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'EXP'
    except jwt.InvalidTokenError:
        return 'INV'

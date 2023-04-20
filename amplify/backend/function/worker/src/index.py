import json
import boto3
import uuid
import os
import requests
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError


dbb = boto3.resource('dynamodb',region_name='eu-west-1')
s3_client = boto3.client('s3')


def handler(event, context):
    print(event)
    response = {}
    uuid = json.loads(event.get('Records')[0].get('body')).get('id')
    print(uuid)
    tableName = os.environ['STORAGE_DYNAMOBTP_NAME']
    bucket = os.environ['STORAGE_STORAGEAWS_BUCKETNAME']
    table = dbb.Table(tableName)

    user = get_user(user_id=uuid, table=table)
    fileUploded = upload_file(json.dumps(user),uuid, bucket, object_name=None)
#     data = get_url(bucket, f"user/{uuid}/info.json")

    if not fileUploded:
      raise ValueError('File not uploaded')

    webhook = user['user']['webhook']

    # Set the headers
    headers = {}
    headers['Content-Type'] = "application/json"

    # Send the request
#     req = requests.post(webhook, data=data, headers=headers)

    response['statusCode'] = 200


def get_user(user_id, table):
    print(user_id)
    user = table.get_item(
    Key={'id': user_id},
    ProjectionExpression="firstname,lastname, age, email, webhook"
    )
    print(user)
    print(user['Item'])

    return { 'user': user['Item'] }


def upload_file(file_name,user_id, bucket, object_name=None):

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.put_object(Body=file_name, Bucket=bucket, Key=f'user/{user_id}/info.json')
    except ClientError as e:
        logging.error(e)
        return False
    return True


# def get_url(bucket, object_name):
#     # Generate the URL to get 'key-name' from 'bucket-name'
#     url = s3_client.generate_presigned_url('get_object',
#                                            Params={'Bucket': bucket,
#                                                    'Key': object_name},
#                                            ExpiresIn=3600)
#     return {"url":url}
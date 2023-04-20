import json
import boto3
import requests

from botocore.exceptions import ClientError

s3_client = boto3.client('s3')

def handler(event, context):
    response = {}
    print(event)
    records = event.get('Records')[0]
    event_name = records.get('eventName')
    if not event_name == 'ObjectCreated:Put':
      raise ValueError('Wrong event')

    file_name = records.get('s3').get('object').get('key')
    print(file_name)
    bucket = records.get('s3').get('bucket').get('name')
    print(bucket)

    webhook = get_webhook(bucket, file_name)

    data = get_url(bucket, file_name)

    # Set the headers
    headers = {}
    headers['Content-Type'] = "application/json"

    # Send the request

    req = requests.post(webhook, json=data, headers=headers)

    response['statusCode'] = 200




def get_webhook(bucket, file_name):
    try:
        response = s3_client.get_object(Bucket=bucket, Key=file_name)
        byte_string = response['Body'].read()
        string_data = byte_string.decode()
        json_data = json.loads(string_data)
        webhook = json_data['user']['webhook']

    except ClientError as e:
        logging.error(e)
        return False

    return webhook

def get_url(bucket, object_name):
    # Generate the URL to get 'key-name' from 'bucket-name'
    url = s3_client.generate_presigned_url('get_object',
                                           Params={'Bucket': bucket,
                                                   'Key': object_name},
                                           ExpiresIn=3600)
    return {"url":url}

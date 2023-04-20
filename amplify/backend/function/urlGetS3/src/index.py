import json
import boto3
import uuid
import os
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

dbb = boto3.resource('dynamodb',region_name='eu-west-1')
s3_client = boto3.client('s3')

def handler(event, context):
  response = {}

  try:
    httpMethod = event.get('httpMethod')
    if not httpMethod or httpMethod != 'GET':
      raise ValueError('Wrong Rest Method')

    param = event.get('queryStringParameters') or {}
    user_id = param.get('id')

    if not user_id:
      raise ValueError('Missing user id')

    tableName = os.environ['STORAGE_DYNAMOBTP_NAME']
    bucket = os.environ['STORAGE_STORAGEAWS_BUCKETNAME']
    table = dbb.Table(tableName)

    user = json.dumps(get_user(user_id=user_id, table=table))

    fileUploded = upload_file(user,user_id, bucket, object_name=None)

    if not fileUploded:
      raise ValueError('File not uploaded')

    response['body'] = json.dumps(get_url(bucket, f"user/{user_id}/info.json"))
    response['statusCode'] = 200


  except (Exception, ClientError) as err:
    print(err)
    response['statusCode'] = 400
    response['body'] = { 'error': str(err) }

  return response



def get_user(user_id, table):
  user = table.get_item(
    Key={'id': user_id},
    ProjectionExpression="firstname,lastname, age, email"
  )

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

def get_url(bucket, object_name):
    # Generate the URL to get 'key-name' from 'bucket-name'
    url = s3_client.generate_presigned_url('get_object',
                                           Params={'Bucket': bucket,
                                                   'Key': object_name},
                                           ExpiresIn=3600)
    return {"url":url}
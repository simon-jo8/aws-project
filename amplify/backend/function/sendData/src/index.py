import json
import boto3
import uuid
import os
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

dbb = boto3.resource('dynamodb',region_name='eu-west-1')
sm = boto3.client('secretsmanager', region_name='eu-west-1')
sqs = boto3.client('sqs',region_name='eu-west-1')


def handler(event, context):
  response = {}
  try:
    httpMethod = event.get('httpMethod')
    if not httpMethod or httpMethod != 'GET':
      raise ValueError('Wrong Rest Method')

    param = event.get('queryStringParameters') or {}
    secret = param.get('id')
    webhook = param.get('webhook')

    if not secret:
      raise ValueError('Missing user id')

    if not webhook:
      raise ValueError('Missing webhook')

    response

    tableName = os.environ['STORAGE_DYNAMOBTP_NAME']
    table = dbb.Table(tableName)

    user_id = get_secret(secret)
    queue_url = 'https://sqs.eu-west-1.amazonaws.com/341557181128/queueSimon'

    webhookUpdated = updateTable(user_id, webhook,table)
    if not webhookUpdated:
      raise ValueError('Webhook not updated')

    sqsResponse = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody= json.dumps({'id': user_id })
    )
    print(sqsResponse)
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



def get_secret(secretKey):
    try:
        response = sm.get_secret_value(
            SecretId='user',
        )
    except ClientError as e:
      raise ValueError(str(e))

    return json.loads(response['SecretString'])[secretKey]

def updateTable(user_id, webhook,table):
    try:
        response = table.update_item(
            Key={
                'id': user_id
            },
            UpdateExpression="set webhook = :w",
            ExpressionAttributeValues={
                ':w': webhook
            }
        )
        return True

    except ClientError as e:
      raise ValueError(str(e))
      return False


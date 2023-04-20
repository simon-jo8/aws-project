import json
import uuid
import boto3
import os
from botocore.exceptions import ClientError

ddb = boto3.resource('dynamodb',region_name='eu-west-1')

def handler(event, context):
    id = event.get('id')
    data = event.get('data')

    try:
        table = ddb.Table(os.environ['STORAGE_FOOBAR_NAME'])
        table.put_item(
            Item={
                'id': id,
                'data': data
            }
        )
        return "OK"
    except (Exception,ClientError) as e:
        print(e)
        raise ValueError(str(e))



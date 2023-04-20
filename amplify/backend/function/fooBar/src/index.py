import json
import uuid

def handler(event, context):
    body = event.get('body')
    data = body.get('data')
    result = []

    for elm in data:
        result.append({
            'id': str(uuid.uuid4()),
            'data': elm
        })

    return result
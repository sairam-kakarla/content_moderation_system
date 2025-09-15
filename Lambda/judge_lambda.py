import json
import boto3
import os
import uuid
from datetime import datetime, timezone

 # Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
sqs_client = boto3.client('sqs')
TABLE_NAME=os.environ['TABLE_NAME']
QUEUE_URL=os.environ['QUEUE_URL']

def lambda_handler(event, context):
    try:
        body=json.loads(event.get('body','{}'))
    except json.JSONDecodeError:
        return {
            'statusCode':400,
            'body':json.dumps({'error':'Invalid JSON in request body'}) 
        }
    if 'comment' not in body:
        return {
            'statusCode':400,
            'body':json.dumps({'error':'Missing comment in request body'})
        }
    user_comment=body['comment']
    job_id=str(uuid.uuid4())
    created_at=datetime.now(timezone.utc).isoformat()
    sqs_message={
        'job_id':job_id,
        'comment':user_comment
    }
    db_item={
        'job_id':job_id,
        'comment':user_comment,
        'created_at':created_at,
        'status':'pending',
        'result':{},
        'error':None
    }
    try:
        table=dynamodb.Table(TABLE_NAME)
        table.put_item(Item=db_item)
        sqs_client.send_message(QueueUrl=QUEUE_URL,MessageBody=json.dumps(sqs_message))
        return {
            'statusCode':200,
            'body':json.dumps({'job_id':job_id})
        }
    except Exception as e:
        return {
            'statusCode':500,
            'body':json.dumps({'error':str(e)})
        }

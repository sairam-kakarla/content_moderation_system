import json
import os
import google.generativeai as genai
import time
import boto3
from gemini_helper import analyze_comment
from decimal import Decimal
google_api_key = os.environ.get('GOOGLE_API_KEY')
try:
    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    dynamodb=boto3.resource('dynamodb')
    table_name = os.environ.get('TABLE_NAME')
    sqs = boto3.client('sqs')
    sqs_queue_url = os.environ.get('QUEUE_URL')
    table=dynamodb.Table(table_name)
except Exception as e:
    print(f"Error: {e}")
    exit(1)
def lambda_handler(event, context):
    for message in event['Records']:
        try:
            body=json.loads(message['body'])
            job_id=body['job_id']
            comment=body['comment']
            result=analyze_comment(comment,model)

            if result is not None:
                table.update_item(
                    Key={'job_id': job_id},
                    UpdateExpression='SET job_result = :res, job_status = :st',
                    ExpressionAttributeValues={
                        ':res': result,
                        ':st': 'COMPLETED'
                        }
                    )
                sqs.delete_message(QueueUrl=sqs_queue_url, ReceiptHandle=message['receiptHandle'])
            else:
                sqs.change_message_visibility(QueueUrl=sqs_queue_url, ReceiptHandle=message['receiptHandle'], VisibilityTimeout=3600)
        except Exception as e:
            print(f"Error: {e}")
            raise e
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete.')
    }

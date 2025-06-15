import json
import base64
import boto3
import os

s3 = boto3.client('s3')
BUCKET = os.environ.get('UPLOAD_BUCKET')

def lambda_handler(event, context):
    # Parse JSON body safely
    data = event.get('bodyJson') or json.loads(event.get('body', '{}'))
    
    try:
        filename = data['filename']
        content = data['content']  # base64-encoded image
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing filename or content')
        }
    
    # New filter: reject filenames with "_NOP_"
    if '_NOP_' in filename:
        return {
            'statusCode': 400,
            'body': json.dumps('Filename not allowed to contain "_NOP_"')
        }

    # Validate file extension
    valid_ext = ('.png', '.jpg', '.jpeg')
    if not filename.lower().endswith(valid_ext):
        return {
            'statusCode': 400,
            'body': json.dumps(f'Invalid file type, only {", ".join(valid_ext)} allowed')
        }

    # Decode content and upload to S3
    try:
        decoded = base64.b64decode(content)
        s3.put_object(Bucket=BUCKET, Key=filename, Body=decoded)
        return {
            'statusCode': 200,
            'body': json.dumps('Upload Success')
        }
    except Exception as e:
        print("Error:", e)
        return {
            'statusCode': 500,
            'body': json.dumps('Internal Server Error')
        }

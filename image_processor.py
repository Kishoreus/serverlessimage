import os
import boto3
from PIL import Image, ImageFilter
import urllib.parse

s3 = boto3.client('s3')
TARGET_BUCKET = os.environ.get('OUTPUT_BUCKET')

def lambda_handler(event, context):
    for rec in event.get('Records', []):
        try:
            src_bucket = rec['s3']['bucket']['name']
            key = urllib.parse.unquote_plus(rec['s3']['object']['key'])
            base_name = os.path.basename(key)
            name, ext = os.path.splitext(base_name)
            
            download_path = f'/tmp/{base_name}'
            processed_name = f"{name}_NOP{ext}"
            upload_path = f'/tmp/{processed_name}'

            # Download original image
            s3.download_file(src_bucket, key, download_path)

            # Process image (resize + edge filter)
            with Image.open(download_path) as img:
                img.thumbnail((800, 800))
                img = img.filter(ImageFilter.EDGE_ENHANCE)
                img.save(upload_path)

            # Upload processed image
            dest_key = f'processed-{processed_name}'
            s3.upload_file(upload_path, TARGET_BUCKET, dest_key)
            print(f'Successfully uploaded to {TARGET_BUCKET}/{dest_key}')

        except Exception as e:
            print("Failed processing:", e)
            raise e

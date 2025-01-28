# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import json
import urllib.parse
import boto3

print('Loading function')

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('mymetadata')

def get_image_metadata(image_id):
    try:
        response = table.get_item(
            Key={
                'ImageID': image_id
            }
        )
        if 'Item' in response:
            return response['Item']
        else:
            return None
    except Exception as e:
        print(f"Error retrieving metadata: {e}")
        return None
def get_all_metadata():
    try:
        response = table.scan()
        return response['Items']
    except Exception as e:
        print(f"Error retrieving metadata: {e}")
        return None

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    # Check if the event is from S3 or API Gateway
    if 'Records' in event:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        try:
            response = s3.get_object(Bucket=bucket, Key=key)
            print("CONTENT TYPE: " + response['ContentType'])
        except Exception as e:
            print(e)
            print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
            raise e
        # Define metadata
        metadata = {
            'artist': 'Artist Name',
            'copyright': '2025 Artist Name',
            'description': 'Image description'
        }
        
        try:
            # Copy the object to the same bucket with new metadata
            copy_source = {'Bucket': bucket, 'Key': key}
            s3.copy_object(
                Bucket=bucket,
                CopySource=copy_source,
                Key=key,
                Metadata=metadata,
                MetadataDirective='REPLACE'
            )

            table.put_item(
                Item={
                    'ImageID': key,
                    'ArtistName': metadata['artist'],
                    'Copyright': metadata['copyright'],
                    'Description': metadata['description']
                }
            )
            
            return {
                'statusCode': 200,
                'body': json.dumps('Metadata and dynamo added successfully!')
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f'Error adding metadata: {e}')
            }
    else:
        # API Gateway event
        image_id = event['ImageId']
        metadata = get_image_metadata(image_id)
        #metadata = get_all_metadata()
        if metadata:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(metadata)
            }
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Image not found'})
            }


        

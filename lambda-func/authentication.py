import boto3
import urllib.parse

# Define your AWS services
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
Table = dynamodb.Table('facerecognition')
print("function fired")

def lambda_handler(event, context):
    print("Received event:", event)

    # Extract the object key from the S3 event
    object_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    print("Object key:", object_key)

    try:
        # Retrieve image bytes from S3
        image_bytes = s3.get_object(Bucket='doorbell-images1', Key=object_key)['Body'].read()

        # Perform face search with Rekognition
        response = rekognition.search_faces_by_image(
            CollectionId='facerecognition_collection',
            Image={'Bytes': image_bytes}
        )

        # Process face matches
        for match in response.get('FaceMatches', []):
            face_id = match['Face']['FaceId']

            # Retrieve additional information from DynamoDB
            try:
                face = Table.get_item(
                    Key={
                        'RekognitionId': face_id
                    }
                )

                if 'Item' in face:
                    full_name = face['Item'].get('FullName', 'Unknown')
                    print('Person Found:', full_name)
                    return {'status': 'success', 'message': f'Person Found: {full_name}'}
                else:
                    print('Person not found in DynamoDB for RekognitionId:', face_id)

            except Exception as e:
                print(f'Error getting item from DynamoDB: {str(e)}')

        # If no face is found
        print('No person found in the photo.')
        return {'status': 'success', 'message': 'No person found in the photo.'}

    except Exception as e:
        print(f'Error: {str(e)}')
        # Handle the error, for example, by returning an appropriate response
        return {'status': 'error', 'message': f'Error: {str(e)}'}

# Add any additional logic or error handling as needed.

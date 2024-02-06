import boto3
import urllib.parse

# Define your AWS services
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
Table = dynamodb.Table('facerecognition')
sns = boto3.client("sns")

def lambda_handler(event, context):
    print("Received event:", event)

    # Extract the object key from the S3 event
    object_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    print("Object key:", object_key)

    try:
        # Retrieve image bytes from S3
        image_bytes = s3.get_object(Bucket='doorbell-images1', Key=object_key)['Body'].read()

        # Perform face detection with Rekognition
        response = rekognition.search_faces_by_image(
            CollectionId='facerecognition_collection',
            Image={'Bytes': image_bytes}
        )

        face_found = False
        for match in response['FaceMatches']:
            print(match['Face']['FaceId'], match['Face']['Confidence'])

            # Corrected line: Use the Table object to get the item
            face = Table.get_item(
            Key={'RekognitionId': match['Face']['FaceId']}
            )

            if 'Item' in face:
                name = face['Item']['FullName']
                
                print(name, " is at the door")
                
                message = sns.publish(
                    TopicArn='arn:aws:sns:eu-central-1:271914456393:DoorbellNotification',
                    Message=f'{name} is at the door'
                )
                
                face_found = True
                break
        
        if not face_found:
            print('Unauthorized person at door')
            message = sns.publish(
                    TopicArn='arn:aws:sns:eu-central-1:271914456393:DoorbellNotification',
                    Message='Unauthorized person at the door'
                )

    except Exception as e:
        print(f'Error: {str(e)}')
        
        message = sns.publish(
                TopicArn='arn:aws:sns:eu-central-1:271914456393:DoorbellNotification',
                Message='Doorbell ringed but no faces detected'
            )
        
    return {'status': 'error', 'message': f'Error: {str(e)}'}
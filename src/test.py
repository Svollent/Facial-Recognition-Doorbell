import cv2
import pathlib
import boto3
from botocore.exceptions import NoCredentialsError

# Initialize AWS Rekognition client
aws_access_key_id = 'AKIAT6T25KVE6Q5L5CED'
aws_secret_access_key = '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'
region_name = 'eu-central-1'
rekognition_client = boto3.client('rekognition', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)

dynamodb = boto3.client('dynamodb', region_name=region_name)
# OpenCV VideoCapture
webcam = cv2.VideoCapture(0)

face_detected = False
stability_count = 0
stability_threshold = 30  # how many frames until a face is considered stable

while True:
    _, frame = webcam.read()

    frame = cv2.flip(frame, 1)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Your cascade classifier initialization
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    clf = cv2.CascadeClassifier(cascade_path)

    faces = clf.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE)

    num_faces = len(faces)

    if num_faces == 1:
        if face_detected == False:
            face_detected = True
            stability_count = 0
        else:
            stability_count += 1
            if stability_count >= stability_threshold:
                cv2.imwrite("face.jpg", frame)
                print("Face Detected, Picture taken")

                # Use AWS Rekognition to check for faces
                with open("face.jpg", "rb") as image_file:
                    image_binary = image_file.read()

                    response = rekognition_client.search_faces_by_image(
                        CollectionId='facerecognition_collection',
                        Image={'Bytes': image_binary}
                    )

                    found = False
                    for match in response['FaceMatches']:
                        print(match['Face']['FaceId'], match['Face']['Confidence'])

                        face_id = match['Face']['FaceId']
                        face = dynamodb.get_item(
                            TableName='facerecognition',
                            Key={'RekognitionId': {'S': face_id}}
                        )

                        if 'Item' in face:
                            print("Found Person: ", face['Item']['FullName']['S'])
                            found = True

                    if not found:
                        print("Face not Authorized")

                stability_count = 0

    else:
        if num_faces > 1 and face_detected == True:
            print("Too many faces detected")
        elif num_faces <= 0 and face_detected == True:
            face_detected = False
            print("No faces detected")

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)

    cv2.imshow("Faces", frame)
    if cv2.waitKey(1) == ord("q"):
        break

webcam.release()
cv2.destroyAllWindows()
import cv2
from datetime import datetime
import boto3
import os

cap = cv2.VideoCapture(0)

# Set the resolution of the captured video
cap.set(3, 1280)
cap.set(4, 720)

s3 = boto3.client('s3')

bucket = 'doorbell-images1'

imagepath = r"C:\Coding\rekog-doorbell\Doorbell-Images"

while True:
    ret, frame = cap.read()

    key = cv2.waitKey(1)
    
    if key == ord(" "):
        
        #Creates image, naming the based on the time it was taken
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filepath = os.path.join(imagepath, f"{timestamp}.jpg")
        cv2.imwrite(filepath, frame)

        #Uploads the Picture taken to the s3 bucket
        s3.upload_file(filepath, bucket, f'{timestamp}.jpg')

    cv2.imshow("Doorbell Camera", frame)

    # If q is pressed the program shuts down
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
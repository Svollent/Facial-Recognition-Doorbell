import cv2
from datetime import datetime
import boto3
import os

cap = cv2.VideoCapture(0)

cap.set(3, 1280)
cap.set(4, 720)

s3 = boto3.client('s3')
bucket = 'doorbell-images1'

while True:
    ret, frame = cap.read()

    key = cv2.waitKey(1)
    
    if key == ord(" "):


        c = datetime.now()

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        print(timestamp)

        cv2.imwrite(f"{timestamp}.jpg", frame)

        s3.upload_file(f'{timestamp}.jpg', 'doorbell-images1', f'{timestamp}.jpg')

        print(f"Image saved as {timestamp}.jpg")

    cv2.imshow("frame", frame)

    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
import cv2
from datetime import datetime
import boto3
import os
import winsound

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

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    clf = cv2.CascadeClassifier(cascade_path)

    faces = clf.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE)
    
    if key == ord(" "):
        
        #just plays a sound to indicate doorbell has been pressed
        winsound.PlaySound("n", 0)
        #Creates image, naming the based on the time it was taken
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filepath = os.path.join(imagepath, f"{timestamp}.jpg")
        cv2.imwrite(filepath, frame)
        print(f"{timestamp} saved to {imagepath}")

        #Uploads the Picture taken to the s3 bucket
        s3.upload_file(filepath, bucket, f'{timestamp}.jpg')

    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
    
    cv2.imshow("Doorbell Camera", frame)

    # If q is pressed the program shuts down
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
# import the necessary packages
from __future__ import print_function
import cv2
import processor as pc

cap = cv2.VideoCapture(0)
processor = pc.Processor(cv2)
while(True):
    ret, image = cap.read()
    #image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    image = processor.processImage(image)

    cv2.imshow('frame', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
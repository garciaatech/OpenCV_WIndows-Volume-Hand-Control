import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#set webcam height and width
wCam, hCam = 640,480

#select what camera to use (usually default to 0 if unknown)
cap = cv2.VideoCapture(0)

#set IDs to height and width
cap.set(3,wCam)
cap.set(4,hCam)

#set time variable
pTime = 0

#object from handtracker #change detection confidence
detector = htm.handDetector(detectionCon=0.7)

#pycaw volume control https://github.com/AndreMiras/pycaw
#initialization
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

#volume manipulation
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()

#set max and min volume
minVol = volRange[0]
maxVol = volRange[1]
vol=0
volBar=400
volPer=0

while True:
    #check for webcam success and read webcam
    success, img =  cap.read()

    #find hand and give it an image and return the drawn image
    img = detector.findHands(img)

    #find position of fingers
    lmList = detector.findPostion(img, draw=False)

    #check for points
    if len(lmList) != 0:
        #get postion of certain point
        #print(lmList[4], lmList[8]) #from mediapipe hand image

        #create variables for lmlist
        x1,y1 = lmList[4][1],lmList[4][2]
        x2,y2 = lmList[8][1], lmList[8][2]
        #get center of line
        cx,cy = (x1+x2)//2,(y1+y2)//2

        #create circle to check if correct finger selected
        cv2.circle(img,(x1,y1),10,(100,10,0),cv2.FILLED)
        cv2.circle(img,(x2,y2),10,(100,10,0),cv2.FILLED)
        #create a line to connect them
        cv2.line(img,(x1,y1),(x2,y2),(100,10,0),3)
        #create circle at center of line
        cv2.circle(img, (cx,cy), 10, (100, 10, 0), cv2.FILLED)

        #get length of line
        length  = math.hypot(x2-x1,y2-y1)
        #print(length)

        #change color depending on length of line
        if length<30:
            cv2.circle(img, (cx, cy), 10, (10, 100, 0), cv2.FILLED)

        #create volume bar
        cv2.rectangle(img,(50,150),(85,400),(0,100,250),3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 100, 250), cv2.FILLED)
        #display percentage
        cv2.putText(img, f'{int(volPer)}%', (40, 450), cv2.FONT_HERSHEY_PLAIN, 3, (0, 100, 250), 3)

        #hand range from 50 to 300
        #volume range -96 to 0

        #use numpy  to convert range from 30,300 to -96,0
        vol = np.interp(length,[30,100],[minVol,maxVol])
        #convert volume for bar to match other rectangle
        volBar = np.interp(length, [30, 100], [400, 150])
        #convert for percentage
        volPer = np.interp(length, [30, 100], [0, 100])

        #manipulate volume with hand
        volume.SetMasterVolumeLevel(vol, None)

    #get position
    lmList =  detector.findPostion(img, draw=False)

    #create framerate
    cTime = time.time() #get current time
    fps = 1/(cTime-pTime) #formula to get fps
    pTime = cTime #change previous time to current time

    #display fps
    cv2.putText(img,f'FPS: {int(fps)}', (40, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0), 3)

    #show the image
    cv2.imshow("img", img)

    #delay for one millisecond
    cv2.waitKey(1)
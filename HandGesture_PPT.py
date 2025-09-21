import cv2
import os
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# Variables
width, height = 1280, 720
folderPath = "Presentation Dummy"

# Camera Setup
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(2, height)

# Get List of Presentation Images
pathImages = sorted(os.listdir(folderPath), key = len)
# print(pathImages)

# Variables
imgNumber = 0
hs, ws = int(100*1), int(170*1)
gestureThreshold = 500
buttonPressed = False
buttonCounter = 0
buttonDelay = 10
annotations = [[]]
annotationNumber = -1
annotationStart = False
# zoomScale = 1.0
# zoomFactor = 0.1

# Hand Detector
detector = HandDetector(detectionCon = 0.5, maxHands = 1)

while True:
    # Import Images
    success, img = cap.read()
    img = cv2.flip(img, 1)
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)
    
    # Gesture Thereshold
    hands, img = detector.findHands(img)
    cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 10)
    
    if hands and buttonPressed is False:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx, cy = hand['center']
        # print(fingers)
        
        lmList = hand['lmList']
        
        # Constraint Values for easier drawing
        # indexFinger = lmList[8][0], lmList[8][1]
        
        # 0: Wrist
        # 1-4: Thumb (various joints and tip)
        # 5-8: Index finger (various joints and tip)
        # 9-12: Middle finger (various joints and tip)
        # 13-16: Ring finger (various joints and tip)
        # 17-20: Pinky finger (various joints and tip)
        
        xVal = int(np.interp(lmList[8][0], [width // 2, w], [0, width]))
        yVal = int(np.interp(lmList[8][1], [150, height - 150], [0, height]))
        indexFinger = xVal, yVal
        
        if cy <= gestureThreshold: # If hand is at the height of the face
            
            # Gesture 1 - Left
            if fingers == [1, 0, 0, 0, 0]:
                # print('left')
                if imgNumber > 0:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False
                    imgNumber -= 1
            
            # Gesture 2 - Right
            if fingers == [0, 0, 0, 0, 1]:
                # print('right')
                if imgNumber < len(pathImages) - 1:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False
                    imgNumber += 1
    
        # Gesture 3 - Show Pointer
        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)

        # Gesture 4 - Draw
        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            annotations[annotationNumber].append(indexFinger)
        else:
            annotationStart = False
    
        # Gesture 5 - Erase
        if fingers == [0, 1, 1, 1, 0]:
            if annotations:
                annotations.pop(-1)
                annotationNumber -= 1
                buttonPressed = True
                
        # Gesture 6 - Erase All
        if fingers == [0, 1, 0, 0, 1]:
            annotations = [[]]
            annotationNumber = -1
            annotationStart = False
            
    #     # Gesture 7 - Zoom In
    #     if fingers == [1, 1, 0, 0, 0]:
    #         zoomScale = min(2.0, zoomScale + zoomFactor)
    #         buttonPressed = True

    #     # Gesture 8 - Zoom Out
    #     if fingers == [1, 0, 1, 0, 0]:
    #         zoomScale = max(1.0, zoomScale - zoomFactor)
    #         buttonPressed = True
    
    # h, w, _ = imgCurrent.shape
    # centerX, centerY = w // 2, h // 2
    # zoomedWidth, zoomedHeight = int(w * zoomScale), int(h * zoomScale)
    # topLeftX, topLeftY = centerX - zoomedWidth // 2, centerY - zoomedHeight // 2
    # bottomRightX, bottomRightY = centerX + zoomedWidth // 2, centerY + zoomedHeight // 2

    # imgCurrent = cv2.resize(imgCurrent[topLeftY:bottomRightY, topLeftX:bottomRightX], (w, h))
    
    # Button Pressed iteration
    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed = False
    
    for i in range(len(annotations)):
        for j in range(len(annotations[i])):
            if j != 0:
                cv2.line(imgCurrent, annotations[i][j-1], annotations[i][j], (0, 0, 200), 12)
    
    # Adding Webcam Image on Slides
    imgSmall = cv2.resize(img, (ws, hs))
    h, w, _ = imgCurrent.shape
    imgCurrent[0:hs, w-ws:w] = imgSmall
    
    cv2.imshow('Image', img)
    cv2.imshow('Slides', imgCurrent)
    
    key = cv2.waitKey(1)
    if key == ord('x'):
        break


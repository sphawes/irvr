import cv2
import time
import math
import serial
import numpy as np
import threading
import json
import sys
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

port = '/dev/cu.wchusbserial1410'
ser = serial.Serial(port, 115200)
font = cv2.FONT_HERSHEY_SIMPLEX
hsvLower = (79, 95, 50)
hsvUpper = (157, 255, 255)
w = 640.0
minRadius = 10
buffer_string = ''
last_received = ''


posX = 0
posY = 0
posZ = 0

imuX = 0
imuY = 0
imuZ = 0

joyX = 0
joyY = 0
joyB = 0

trig1 = 0
trig2 = 0
a = 0
b = 0

#connect to webcam
capture = cv2.VideoCapture(0)
print capture.get(cv2.CAP_PROP_FPS)

while True:
    #take image from webcam
    ret, image = capture.read()

    #scaling down for faster processing
    img_height, img_width, depth = image.shape
    scale = w / img_width
    h = img_height * scale
    image = cv2.resize(image, (0,0), fx=scale, fy=scale)
    scaledHeight, scaledWidth, scaledDepth = image.shape

    #image processing
    blurred = cv2.GaussianBlur(image, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, hsvLower, hsvUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    #find contours
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None

	# only proceed if at least one contour was found
    if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# only proceed if the radius meets a minimum size
        if radius > minRadius:

            cv2.circle(image, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(image, center, 5, (0, 0, 0), -1)

            posX = 100 - int((x / scaledWidth)*100)
            posY = int((y / scaledHeight)*100)
            posZ = int((radius*2) - (minRadius*2))

    #DATA GATHERING
    buffer_string = buffer_string + ser.read(ser.inWaiting())
    if '\n' in buffer_string:
        lines = buffer_string.split('\n') # Guaranteed to have at least 2 entries
        last_received = lines[-2]
        #If the Arduino sends lots of empty lines, you'll lose the
        #last filled line, so you could make the above statement conditional
        #like so: if lines[-2]: last_received = lines[-2]
        buffer_string = lines[-1]

    btList = last_received.split(',')


    if(len(btList) >= 7):
        imuX = int(float(btList[0])*10) #+ ((cv2.getTrackbarPos("Yaw", "Tune IMU") - 180)*10)
        imuY = int(float(btList[1])*10) #+ ((cv2.getTrackbarPos("Pitch", "Tune IMU") - 90)*10)
        imuZ = int(float(btList[2])*10) #+ ((cv2.getTrackbarPos("Roll", "Tune IMU") - 90)*10)

        joyX = btList[3]
        joyY = btList[4]
        joyB = btList[5]

        trig1 = btList[6]
        trig2 = btList[7]
        a = btList[8]
        b = btList[9]


    #prints out all the data gathered from the daemon
    data = str(posX)+str(posY)+str(posZ)+str(imuX)+str(imuY)+str(imuZ)+str(joyX)+str(joyY)+str(joyB)+str(trig1)+str(trig2)+str(a)+str(b)
    print(posX, posY, posZ, imuX, imuY, imuZ, joyX, joyY, joyB, trig1, trig2, a, b)

    #prints flipped image with tracked blob superimposed and positional text overlayed
    image = cv2.flip(image, 1)
    cv2.putText(image, "X: " + str(posX), (5,20), font, .5, (255,255,255), 1, cv2.LINE_AA)
    cv2.putText(image, "Y: " + str(posY), (5,40), font, .5, (255,255,255), 1, cv2.LINE_AA)
    cv2.putText(image, "Z: " + str(posZ), (5,60), font, .5, (255,255,255), 1, cv2.LINE_AA)

    cv2.putText(image, "Yaw: " + str(imuX), (5,80), font, .5, (255,255,255), 1, cv2.LINE_AA)
    cv2.putText(image, "Pitch: " + str(imuY), (5,100), font, .5, (255,255,255), 1, cv2.LINE_AA)
    cv2.putText(image, "Roll: " + str(imuZ), (5,120), font, .5, (255,255,255), 1, cv2.LINE_AA)

    cv2.putText(image, "JoyX: " + str(joyX), (5,140), font, .5, (255,255,255), 1, cv2.LINE_AA)
    cv2.putText(image, "JoyY: " + str(joyY), (5,160), font, .5, (255,255,255), 1, cv2.LINE_AA)
    cv2.putText(image, "JoyB: " + str(joyB), (5,180), font, .5, (255,255,255), 1, cv2.LINE_AA)

    cv2.putText(image, "Trig1: " + str(trig1), (5,200), font, .5, (255,255,255), 1, cv2.LINE_AA)
    cv2.putText(image, "Trig2: " + str(trig2), (5,220), font, .5, (255,255,255), 1, cv2.LINE_AA)
    cv2.putText(image, "A: " + str(a), (5,240), font, .5, (255,255,255), 1, cv2.LINE_AA)
    cv2.putText(image, "B: " + str(b), (5,260), font, .5, (255,255,255), 1, cv2.LINE_AA)

    cv2.imshow('IRVR', image)

    #quits when space bar is pressed
    if cv2.waitKey(1) & 0xFF == ord(' '):
        break

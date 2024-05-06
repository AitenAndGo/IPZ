from PIL import ImageGrab
import numpy as np
import cv2 as cv
import pygetwindow as gw
import pyautogui as mouse
import keyboard
import threading
import time

def turnCar(dir):
    if dir == 'left':
        keyboard.release('d')
        keyboard.press('a')
    elif dir == 'right':
        keyboard.release('a')
        keyboard.press('d')
    elif dir == 'forward':
        keyboard.release('d')
        keyboard.release('a')

def perspective2TopDown(frame):
    perspectivePoints = np.float32([[105,275],[480,275],[216,156],[378,156]])
    for pt in perspectivePoints:
        cv.circle(frame, tuple(pt.astype(np.int32)), 3, (0,0,255), -1)
    # cv.imshow('points', frame)
    topDownPoints = np.float32([[450,650],[650,650],[450,450],[650,450]])
    M = cv.getPerspectiveTransform(perspectivePoints,topDownPoints)
    dst = cv.warpPerspective(frame,M,(1080,720))
    cv.imshow("TopDown", dst)

# get window positions
window_title = "RB_MTR_sim"
window = gw.getWindowsWithTitle(window_title)[0]

left, top, right, bottom = window.left, window.top, window.right, window.bottom

# activate window and press 'w' to drive forward
mouse.click(left + 50, top + 50)
# keyboard.press('w')

# line detection window
width = (right - 7) - (left + 7)
height = (bottom - 7) - (top + 50)
detectionWindow = np.zeros((height, width), dtype='uint8')

leftBottom = (int(0.03 * width), int(0.8 * height))
rightBottom = (int((1 - 0.03) * width), int(0.8 * height))
leftTop = (int(0.1 * width), int(0.45 * height))
rightTop = (int((1 - 0.1) * width), int(0.45 * height))

vertices = [leftBottom, rightBottom, rightTop, leftTop]
vertices = np.array([vertices], dtype=np.int32)

cv.fillConvexPoly(detectionWindow, vertices, 255)
cv.imshow("polygon", detectionWindow)

# carControl_thread = threading.Thread(target=carControl)
# carControl_thread.start()

#loop every frame
while(True):
    img = ImageGrab.grab(bbox=(left + 7, top + 50, right - 7, bottom - 7)) #bbox specifies specific region (bbox= x,y,width,height)
    img_np = np.array(img)
    # cv.imshow('color', img_np)
    frame = cv.cvtColor(img_np, cv.COLOR_RGB2BGR)
    cv.imshow("Frame", frame)
    TopDown = perspective2TopDown(frame)
    if (cv.waitKey(1) & 0xFF) == ord('q'):
        Stop = True
        # carControl_thread.join()
        cv.destroyAllWindows()
        break
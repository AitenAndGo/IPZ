    # todo:     # zabierz ten sleep i dodaj żeby skręcał do czasu aż nie będzie znów tylko jednej drogi
    # todo:     # i może też poprawić to w jaki sposób się zlicza ile jest dróg
    # todo:     # skręcanie zrobić dla kąta a nie min/max
    # todo:     # upgrade całego kodu do wersji na raspberkę
    # todo:     # upgrade kodu na bardziej czytelny
    # todo:     # dodać nowy widok z góry, bardziej przejzryste i rusowanie trajektori na żywo
    
    
    

from PIL import ImageGrab
import numpy as np
import cv2 as cv
import pygetwindow as gw
import pyautogui as mouse
import keyboard
import threading
import time
import random

dir = 0
Stop = False
hold = False
isTurning = False
TurnCarAtCrossroad = None
lock = threading.Lock()

def isCrossroad(img, left, right, forward, lpix, rpix, fpix):
    ra = cv.bitwise_and(img, right)
    la = cv.bitwise_and(img, left)
    fa = cv.bitwise_and(img, forward)

    rp = len(np.argwhere(ra > 0)) / lpix
    lp = len(np.argwhere(la > 0)) / rpix
    fp = len(np.argwhere(fa > 0)) / fpix

    turn = []
    if rp > 0.97:
        turn.append('right')
        # print(right)
    if lp > 0.97:
        turn.append('left')
        # print(left)
    if fp > 0.97:
        turn.append('forward')
        # print(forward)

    return turn 

def roadShape(image):
    blank = np.zeros((image.shape[0], image.shape[1]), dtype='uint8')
    points = np.argwhere(image > 0)
    points[:, [0, 1]] = points[:, [1, 0]]
    points = np.array([points], dtype=np.int32)
    if len(points[0]) >= 3:
        road = cv.fillPoly(blank, points, 255)
        cv.imshow("road", road)
        return road
    else:
        return blank

def calculateDirection(img):
    leftHalf = img[:, :img.shape[1]//2]
    righttHalf = img[:, img.shape[1]//2:]
    Lpoints = np.argwhere(leftHalf > 0)
    Rpoints = np.argwhere(righttHalf > 0)
    dir = (len(Lpoints) - len (Rpoints)) / 1000
    # print(dir)
    return dir

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

def carControl():
    global isTurning
    global hold
    leftTurn = False
    rightTurn = False
    forward = False
    while True and not Stop:
        # print(dir)
        if not hold:
            if isTurning:
                turnCar(TurnCarAtCrossroad)
                time.sleep(1.1)
                with lock:
                    isTurning = False
            elif dir > -6 and not rightTurn:
                turnCar('left')
                rightTurn = True
                leftTurn = False
                forward = False
            elif dir < 6 and not leftTurn:
                turnCar('right')
                rightTurn = False
                leftTurn = True
                forward = False
            elif -6 < dir < 6 and not forward:
                turnCar('forward')
                rightTurn = False
                leftTurn = False
                forward = True
            time.sleep(0.01)


# get window positions
window_title = "RB_MTR_sim"
window = gw.getWindowsWithTitle(window_title)[0]

left, top, right, bottom = window.left, window.top, window.right, window.bottom

# activate window and press 'w' to drive forward
mouse.click(left + 50, top + 50)
keyboard.press('w')

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

# crossroad

# right turn check polygon
leftTurnWindow = np.zeros((height, width), dtype='uint8')

leftBottom = (int(0), int(0.9 * height))
rightBottom = (int((0.1) * width), int(0.9 * height))
leftTop = (int(0), int(0.6 * height))
rightTop = (int((0.1) * width), int(0.6 * height))
vertices = [leftBottom, rightBottom, rightTop, leftTop]
vertices = np.array([vertices], dtype=np.int32)
cv.fillConvexPoly(leftTurnWindow, vertices, 255)
cv.imshow("leftTurn", leftTurnWindow)
leftPixels = len(np.argwhere(leftTurnWindow > 0))

# left turn check polygon
rightTurnWindow = np.zeros((height, width), dtype='uint8')

leftBottom = (int(width), int(0.9 * height))
rightBottom = (int((0.9) * width), int(0.9 * height))
leftTop = (int(width), int(0.6 * height))
rightTop = (int((0.9) * width), int(0.6 * height))
vertices = [leftBottom, rightBottom, rightTop, leftTop]
vertices = np.array([vertices], dtype=np.int32)
cv.fillConvexPoly(rightTurnWindow, vertices, 255)
cv.imshow("rightTurn", rightTurnWindow)
rightPixels = len(np.argwhere(rightTurnWindow > 0))

# go forward check polygon
forwardWindow = np.zeros((height, width), dtype='uint8')

leftBottom = (int(0.48 * width), int(0.3 * height))
rightBottom = (int((0.52) * width), int(0.3 * height))
leftTop = (int(0.43 * width), int(0.45 * height))
rightTop = (int((0.58) * width), int(0.45 * height))
vertices = [leftBottom, rightBottom, rightTop, leftTop]
vertices = np.array([vertices], dtype=np.int32)
cv.fillConvexPoly(forwardWindow, vertices, 255)
cv.imshow("forward", forwardWindow)
forwardPixels = len(np.argwhere(forwardWindow > 0))

 

carControl_thread = threading.Thread(target=carControl)
carControl_thread.start()

#loop every frame
while(True):
    img = ImageGrab.grab(bbox=(left + 7, top + 50, right - 7, bottom - 7)) #bbox specifies specific region (bbox= x,y,width,height)
    img_np = np.array(img)
    frame = cv.cvtColor(img_np, cv.COLOR_BGR2GRAY)
    cv.imshow("grayScale", frame)
    if (cv.waitKey(1) & 0xFF) == ord('q'):
        Stop = True
        carControl_thread.join()
        cv.destroyAllWindows()
        break

    ret, lines = cv.threshold(frame, 50, 255, cv.THRESH_BINARY_INV)
    cv.imshow("threshold", lines)

    # use detectionWindow as mask
    edgesInDetectionWindow = cv.bitwise_and(lines, detectionWindow)
    cv.imshow("edgesInDetectionWindow", edgesInDetectionWindow)

    # draw road shape
    road = roadShape(edgesInDetectionWindow)
    dir = calculateDirection(road)

    # check for crossroads
    turns = isCrossroad(lines, leftTurnWindow, rightTurnWindow, forwardWindow,
                                    leftPixels, rightPixels, forwardPixels)
    if len(turns) <= 1:
        pass
        # isTurning = False
        # print("none")
    elif not isTurning:
        turn = random.choice(turns)
        with lock:
            hold = True
        keyboard.release('w')
        keyboard.release('a')
        keyboard.release('d')
        print('Intersection! turn: ' + turn)
        time.sleep(3)
        keyboard.press('w')
        with lock:
            hold = False
            isTurning = True
            TurnCarAtCrossroad = turn
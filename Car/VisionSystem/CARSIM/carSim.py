from PIL import ImageGrab
import numpy as np
import cv2 as cv
import pygetwindow as gw
import pyautogui as mouse
import threading
import time
# from sklearn.linear_model import LinearRegression

dir = 0
Stop = False

def roadShape(image):
    blank = np.zeros((image.shape[0], image.shape[1]), dtype='uint8')
    points = np.argwhere(image > 0)
    points[:, [0, 1]] = points[:, [1, 0]]
    points = np.array([points], dtype=np.int32)
    # print(points)
    # points = np.rot90(points, k=-1)
    road = cv.fillPoly(blank, points, 255)
    cv.imshow("road", road)
    return road

def calculateDirection(img):
    leftHalf = img[:, :img.shape[1]//2]
    righttHalf = img[:, img.shape[1]//2:]
    Lpoints = np.argwhere(leftHalf > 0)
    Rpoints = np.argwhere(righttHalf > 0)
    dir = (len(Lpoints) - len (Rpoints)) / 1000
    # print(dir)
    return dir

def carControl():
    leftTurn = False
    rightTurn = False
    forward = False
    while True and  not Stop:
        print(dir)
        if dir > 12 and not rightTurn:
            mouse.press('d')
            mouse.keyDown('a')
            rightTurn = True
            leftTurn = False
            forward = False
            print('prawo')
        elif dir < -12 and not leftTurn:
            mouse.press('a')
            mouse.keyDown('d')
            rightTurn = False
            leftTurn = True
            forward = False
            print('lewo')
        elif -12 < dir < 12 and not forward:
            rightTurn = False
            leftTurn = False
            forward = True
            mouse.keyUp('d')
            mouse.keyUp('a')
            print('forward')
        # time.sleep(0.1)


# get window positions
window_title = "RB_MTR_sim"
window = gw.getWindowsWithTitle(window_title)[0]

left, top, right, bottom = window.left, window.top, window.right, window.bottom

# print(f'left: {left}, right: {right}, top: {top}, bottom: {bottom}')

# activate window and press 'w' to drive forward
mouse.click(left + 50, top + 50)
mouse.keyDown('w')

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

    # blur the image for better results
    # blur = cv.GaussianBlur(frame, (5, 5), 5)

    # use edge detection filter    
    # edges = cv.Canny(blur, 120, 160)
    # cv.imshow("edges", edges)

    ret, lines = cv.threshold(frame, 50, 255, cv.THRESH_BINARY_INV)
    cv.imshow("threshold", lines)

    # use detectionWindow as mask
    edgesInDetectionWindow = cv.bitwise_and(lines, detectionWindow)
    cv.imshow("edgesInDetectionWindow", edgesInDetectionWindow)

    # calculate a line in the middle of the road
    # middleLine, x = findMiddleLine(edgesInDetectionWindow)

    # draw road shape
    road = roadShape(edgesInDetectionWindow)
    dir = calculateDirection(road)
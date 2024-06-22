from flask import Flask, render_template, Response
import threading
import cv2
from time import sleep
import RPi.GPIO as GPIO
import numpy as np
import serial
import requests
# from fastai.vision.all import load_learner, PILImage  # for sign recognition

uuid = "malinka"

# GPIO

FORWARD_RIGHT = 16
FORWARD_LEFT = 18
BACKWARD_RIGHT = 11
BACKWARD_LEFT = 13

Motor1Enable_PIN = 32
Motor2Enable_PIN = 33

SERVO_PIN = 12


# Defines

MAX_ANGLE = 60
MAX_LEFT = 150
MAX_RIGHT = 30


# Setup

GPIO.setmode(GPIO.BOARD)

GPIO.setup(FORWARD_RIGHT,   GPIO.OUT)
GPIO.setup(BACKWARD_RIGHT,  GPIO.OUT)
GPIO.setup(FORWARD_LEFT,    GPIO.OUT)
GPIO.setup(BACKWARD_LEFT,   GPIO.OUT)

GPIO.setup(Motor1Enable_PIN,GPIO.OUT)
GPIO.setup(Motor2Enable_PIN,GPIO.OUT)
MOTOR_1 = GPIO.PWM(Motor1Enable_PIN, 1000)
MOTOR_2 = GPIO.PWM(Motor2Enable_PIN, 1000)

MOTOR_1.start(0)
MOTOR_2.start(0)

GPIO.setup(SERVO_PIN,       GPIO.OUT)
SERVO = GPIO.PWM(SERVO_PIN, 50)
SERVO.start(0)

app = Flask(__name__)

camera = cv2.VideoCapture(0)  # Use the PiCamera


# Get camera dimensions
width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

detectionWindow = np.zeros((height, width), dtype='uint8')

leftBottom = (int(0.01 * width), int(0.8 * height))
rightBottom = (int((1 - 0.01) * width), int(0.8 * height))
leftTop = (int(0.01 * width), int(0.3 * height))
rightTop = (int((1 - 0.01) * width), int(0.3 * height))

vertices = [leftBottom, rightBottom, rightTop, leftTop]
vertices = np.array([vertices], dtype=np.int32)

cv2.fillConvexPoly(detectionWindow, vertices, 255)

# crossroad

# right turn check polygon
leftTurnWindow = np.zeros((height, width), dtype='uint8')

leftBottom = (int(0), int(0.1 * height))
rightBottom = (int((0.1) * width), int(0.1 * height))
leftTop = (int(0), int(0.0 * height))
rightTop = (int((0.1) * width), int(0.0 * height))
vertices = [leftBottom, rightBottom, rightTop, leftTop]
vertices = np.array([vertices], dtype=np.int32)
cv2.fillConvexPoly(leftTurnWindow, vertices, 255)
leftPixels = len(np.argwhere(leftTurnWindow > 0))

# left turn check polygon
rightTurnWindow = np.zeros((height, width), dtype='uint8')

leftBottom = (int(width), int(0.1 * height))
rightBottom = (int((0.9) * width), int(0.1 * height))
leftTop = (int(width), int(0.0 * height))
rightTop = (int((0.9) * width), int(0.0 * height))
vertices = [leftBottom, rightBottom, rightTop, leftTop]
vertices = np.array([vertices], dtype=np.int32)
cv2.fillConvexPoly(rightTurnWindow, vertices, 255)
rightPixels = len(np.argwhere(rightTurnWindow > 0))

# go forward check polygon
forwardWindow = np.zeros((height, width), dtype='uint8')

leftBottom = (int(0.2 * width), int(0.15 * height))
rightBottom = (int((0.8) * width), int(0.15 * height))
leftTop = (int(0.2 * width), int(0.25 * height))
rightTop = (int((0.8) * width), int(0.25 * height))
vertices = [leftBottom, rightBottom, rightTop, leftTop]
vertices = np.array([vertices], dtype=np.int32)
cv2.fillConvexPoly(forwardWindow, vertices, 255)
forwardPixels = len(np.argwhere(forwardWindow > 0))


WebImage = np.zeros((int(height), int(width)))


def move_forward(speed):
    MOTOR_1.ChangeDutyCycle(speed)
    MOTOR_2.ChangeDutyCycle(speed)
    GPIO.output(BACKWARD_RIGHT, GPIO.LOW)
    GPIO.output(BACKWARD_LEFT,  GPIO.LOW)
    GPIO.output(FORWARD_RIGHT,  GPIO.HIGH)
    GPIO.output(FORWARD_LEFT,   GPIO.HIGH)

def move_backward(speed):
    MOTOR_1.ChangeDutyCycle(speed)
    MOTOR_2.ChangeDutyCycle(speed)
    GPIO.output(FORWARD_RIGHT,  GPIO.LOW)
    GPIO.output(FORWARD_LEFT,   GPIO.LOW)
    GPIO.output(BACKWARD_RIGHT, GPIO.HIGH)
    GPIO.output(BACKWARD_LEFT,  GPIO.HIGH)



def stop():
    GPIO.output(BACKWARD_RIGHT, GPIO.LOW)
    GPIO.output(BACKWARD_LEFT,  GPIO.LOW)
    GPIO.output(FORWARD_RIGHT,  GPIO.LOW)
    GPIO.output(FORWARD_LEFT,   GPIO.LOW)

def turn(angle):

    if angle < (90 - MAX_ANGLE):
        angle = 90 - MAX_ANGLE
    elif angle > (90 + MAX_ANGLE):
        angle = 90 + MAX_ANGLE


    duty_cycle = 2 + (angle / 18)
    SERVO.ChangeDutyCycle(duty_cycle)
    sleep(0.1)
    SERVO.ChangeDutyCycle(0)

def turnCar(dir):
    turn(80 + (dir))

def perspective2TopDown(frame):
    perspectivePoints = np.float32([[185,310],[483,306],[233,172],[434,172]])
    for pt in perspectivePoints:
        cv2.circle(frame, tuple(pt.astype(np.int32)), 3, (0,0,255), -1)

    topDownPoints = np.float32([[450,650],[650,650],[450,450],[650,450]])
    M = cv2.getPerspectiveTransform(perspectivePoints,topDownPoints)
    dst = cv2.warpPerspective(frame,M,(1080,720))
    return dst

def calculateDirection(img):
    leftHalf = img[:, :img.shape[1]//2]
    righttHalf = img[:, img.shape[1]//2:]
    Lpoints = np.argwhere(leftHalf > 0)
    Rpoints = np.argwhere(righttHalf > 0)
    dir = (len(Lpoints) - len (Rpoints)) / 1000
    # print(dir)
    return dir

def process_frame(frame):
    
    # frame = cv2.flip(frame, 1)
    # frame = cv2.flip(frame, 0)
    
    image_original = frame
    
    # frame = perspective2TopDown(frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(frame, (11, 11), 3)
    ret, frame = cv2.threshold(frame, 30, 255, cv2.THRESH_BINARY_INV)
    # frame = cv2.adaptiveThreshold(frame,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
    #  cv2.THRESH_BINARY_INV,11,2)
    ret, otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # frame = cv2.bitwise_and(frame, detectionWindow)

    # frame = cv2.Laplacian(frame,cv2.CV_64F)
    # kernel = np.ones((5, 5), np.uint8)
    # mask_road = cv2.morphologyEx(frame, cv2.MORPH_CLOSE, kernel)
    # mask_road = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)
    # edges = cv2.dilate(frame,kernel,iterations = 1)
    # lines = cv2.HoughLinesP(edges,1,np.pi/180,100,minLineLength=100,maxLineGap=10)

    # blank = np.zeros_like(frame)
    # if lines is not None:
    #     for line in lines:
    #         x1, y1, x2, y2 = line[0]
    #         cv2.line(image_original, (x1, y1), (x2, y2), (0, 255, 0), 10)
    
    
    otsu = cv2.bitwise_not(otsu)
    return frame

def nextTurn(img, left, right, lpix, rpix):
    ra = cv2.bitwise_and(img, right)
    la = cv2.bitwise_and(img, left)

    rp = len(np.argwhere(ra > 0)) / rpix
    lp = len(np.argwhere(la > 0)) / lpix

    turn = []
    if rp > 0.97:
        return "R"
    elif lp > 0.97:
        return "L"
    else:
        return None 

def endOfRoad(img, forward, fpix):
    fa = cv2.bitwise_and(img, forward)
    fp = len(np.argwhere(fa > 0)) / fpix

    if fp < 0.05:
        return True
    else:
        return False

def hardTurn(direction):
    if direction == "R":
        turn(80 + (MAX_RIGHT))
    elif direction == "L":
        turn(80 + (MAX_LEFT))
    
    
def gen_frames():
    while True:
        succes, frame = camera.read()
        if not succes:
            pass
        else:
            # frame = process_frame(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def webCamera():
    app.run(host='0.0.0.0', port=5000)

def cv2_to_pil(img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = PILImage.create(img_rgb)
    return pil_img

def startCar():
    url = "https://miszczak13.eu.pythonanywhere.com/postCar"
    data = {"uuid": uuid}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
    
        if response.headers.get('Content-Type') == 'application/json':
            print(response.json())
        else:
            print("Odpowiedź nie jest w formacie JSON:", response.text)
    
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Something went wrong: {err}")

def getStatus():

    url = f'https://miszczak13.eu.pythonanywhere.com/get_car_status?uuid={uuid}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Rzuć wyjątek w przypadku błędu HTTP

        try:
            car_status = response.json()  # Spróbuj zdekodować odpowiedź jako JSON
            print(f"UUID: {car_status['uuid']}, isDriving: {car_status['isDriving']}")
        except ValueError:
            print("Niepoprawny format JSON w odpowiedzi")
        except KeyError as e:
            print(f"Brak oczekiwanego klucza 'uuid' lub 'isDriving' w odpowiedzi: {e}")

    except requests.exceptions.RequestException as e:
        print(f"Wystąpił błąd podczas żądania: {e}")

if __name__ == '__main__':
    webCamera() # visualization
    startCar()
    # ser = serial.Serial('/dev/rfcomm0', 115200) # for bluetooth with city lights
    # learn = load_learner('model.pkl')
    Turn = "R"
    try:
        move_forward(75)
        while True:
            status = getStatus()
            # if ser.in_waiting > 0:
                # data = ser.read(ser.in_waiting).decode() #BLUETOOTH
            if status:    
                print("go!")
                move_forward(75)
                succes, frame = camera.read()
                if not succes:
                    pass;
                else:
                    # pil_frame = cv2_to_pil(frame)
                    # # Wykonaj predykcję na ramce
                    # pred, pred_idx, probs = learn.predict(pil_frame)
                    # print(pred)
                    frame = process_frame(frame)
                    _turn = nextTurn(frame, leftTurnWindow, rightTurnWindow, leftPixels, rightPixels)
                    if _turn is not None:
                        Turn = _turn
                    if endOfRoad(frame, forwardWindow, forwardPixels):
                        hardTurn(Turn)
                        print("TURN" + Turn)
                        sleep(1)
                    else:
                        dir = calculateDirection(frame)
                        # print(dir)
                        turnCar(dir)
            else:
                stop()
                print('stop')
                # angle = input("Enter angle (0-180): ")
                # if angle == 'w':
                    # move_forward(90)
                # elif angle == 's':
                    # move_backward(90)
                # elif angle == 'x':
                    # stop()
                # else:
                    # turn(float(angle))
                # move_forward(90)
    except KeyboardInterrupt:
        pass
    finally:
        SERVO.stop()
        GPIO.cleanup()


from flask import Flask, render_template, Response
import threading
import cv2
from time import sleep
import RPi.GPIO as GPIO
import numpy as np


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
leftTop = (int(0.01 * width), int(0.15 * height))
rightTop = (int((1 - 0.01) * width), int(0.15 * height))

vertices = [leftBottom, rightBottom, rightTop, leftTop]
vertices = np.array([vertices], dtype=np.int32)

cv2.fillConvexPoly(detectionWindow, vertices, 255)

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
    turn(80 - (dir * 1.5))

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
    frame = cv2.flip(frame, 0)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.GaussianBlur(frame, (11, 11), 0)
    ret, frame = cv2.threshold(frame, 85, 255, cv2.THRESH_BINARY)

    frame = cv2.flip(frame, 0)
    frame = cv2.Laplacian(frame,cv2.CV_64F)
    # edges = cv2.Canny(laplacian,10,80)
    # kernel = np.ones((5, 5), np.uint8)
    # mask_road = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    # mask_road = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel)
    return frame

def gen_frames():
    while True:
        succes, frame = camera.read()
        if not succes:
            pass
        else:
            frame = process_frame(frame)
            frame = cv2.flip(frame, 0)
            # frame = perspective2TopDown(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.GaussianBlur(frame, (11, 11), 0)
            ret, frame = cv2.threshold(frame, 85, 255, cv2.THRESH_BINARY)
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


if __name__ == '__main__':
    webCamera()

    try:
        # move_forward(60)
        while True:
            # succes, frame = camera.read()
            # if not succes:
            #     pass;
            # else:
            #     # frame = process_frame(frame)
            #     frame = cv2.flip(frame, 0)
            #     # frame = perspective2TopDown(frame)
            #     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #     frame = cv2.GaussianBlur(frame, (11, 11), 0)
            #     ret, frame = cv2.threshold(frame, 85, 255, cv2.THRESH_BINARY)
            #     frame = cv2.bitwise_and(frame, detectionWindow)
            #     dir = calculateDirection(frame)
            #     print(dir)
            #     turnCar(dir)

            angle = input("Enter angle (0-180): ")
            if angle == 'w':
                move_forward()
            elif angle == 's':
                move_backward()
            elif angle == 'x':
                stop()
            else:
                turn(float(angle))
    except KeyboardInterrupt:
        pass
    finally:
        SERVO.stop()
        GPIO.cleanup()
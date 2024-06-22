from flask import Flask, redirect, render_template, request, jsonify, abort, flash
from flask_sqlalchemy import SQLAlchemy
#from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from sqlalchemy import desc ,asc
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, pprint
from datetime import datetime, timedelta
import  os
from os.path import isfile, join
from os import listdir
import json
from io import StringIO
from werkzeug.wrappers import Response
import itertools
import random
import string
#import pytz
import socket

CITY_ID = 0

app = Flask(__name__)
app.secret_key = 'development key'

#os.environ['TZ'] = 'Europe/Warsaw'
#app.config['TZ'] = 'Europe/Warsaw'


SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="miszczak13",
    password="alamakota", # database passowrd hidden
    hostname="miszczak13.mysql.eu.pythonanywhere-services.com",
    databasename="miszczak13$default",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299 # connection timeouts
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # no warning disruptions

db = SQLAlchemy(app)
ma = Marshmallow(app)



class Server(db.Model):
    __tablename__ = "server"
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    car_id = db.Column(db.Integer)
    city_id = db.Column(db.Integer)
    startTime = db.Column(db.DATETIME)
    stopTime = db.Column(db.DATETIME)

    def __init__(self,car_id,city_id,startTime,stopTime):
       # self.id = id
        self.car_id = car_id
        self.city_id = city_id
        self.startTime = startTime
        self.stopTime = stopTime

class ServerSchema(ma.Schema):
    class Meta:
        fields = ('id' ,'car_id', 'city_id','startTime','stopTime')
server_schema = ServerSchema()
servers_schema = ServerSchema(many=True)


class Car(db.Model):
    __tablename__ = "car"
    id = db.Column(db.Integer,primary_key=True)
    uuid = db.Column(db.String(4096))
    isDriving = db.Column(db.Boolean)


    def __init__(self,uuid,isDriving):
        self.uuid = uuid
        self.isDriving = isDriving


class CarSchema(ma.Schema):
    class Meta:
        fields = ('id' ,'uuid', 'isDriving')

car_schema = CarSchema()
cars_schema = CarSchema(many=True)

class City_Trafic(db.Model):
    __tablename__ = "city_trafic"
    id = db.Column(db.Integer,primary_key=True)
    car_id = db.Column(db.Integer)
    timeofstop = db.Column(db.DATETIME)
    sensor_id = db.Column(db.Integer)

    def __init__(self,car_id,timeofstop,sensor_id):
        self.car_id = car_id
        self.timeofstop = timeofstop
        self.sensor_id = sensor_id

class City_TraficSchema(ma.Schema):
    class Meta:
        fields = ('id' ,'car_id', 'timeofstop', 'sensor_id')

trafic_schema = City_TraficSchema()
trafics_schema = City_TraficSchema(many=True)

def get_data_from_database():
    # Pobranie danych z tabeli Server
    servers = Server.query.all()
    servers_data = servers_schema.dump(servers)

    # Pobranie danych z tabeli Car
    cars = Car.query.all()
    cars_data = cars_schema.dump(cars)

    # Pobranie danych z tabeli City_Trafic
    traffics = City_Trafic.query.all()
    traffics_data = trafics_schema.dump(traffics)

    return servers_data, cars_data, traffics_data


# wszystkie 3 tablice wyswietlane
@app.route('/')
def hello_world():
    # Pobranie danych z trzech tabel
    servers_data, cars_data, traffics_data = get_data_from_database()
    # Przekazanie danych do szablonu HTML i wyrenderowanie strony
    return render_template('strona_glowna.html', title='Strona główna', table1_data=servers_data, table2_data=cars_data, table3_data=traffics_data)


# po naciśnięciu start samochód zostaje dodany do bazy i zaczyna jechać

@app.route("/postCar", methods=["POST"])
def post_car():
    # POST z raspberry na serwer
    # id = request.json["id"]
    uuid = request.json["uuid"]
    new_car = Car(uuid, False)
    db.session.add(new_car)
    db.session.commit()  # PK increment
    car = Car.query.get(new_car.id)
    return car_schema.jsonify(car)



######################################
# TUTAJ COŚ JEST Z TĄ DATĄ NIE TO CO TRZEBA

def start_driving(car_id):
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_server_record = Server(car_id=car_id, city_id=CITY_ID, startTime=current_time, stopTime=None)
        db.session.add(new_server_record)
        db.session.commit()
        return {"message": "Driving started successfully."}, 200
    except Exception as e:
        db.session.rollback()  # Wycofaj zmiany w przypadku błędu
        return {"error": str(e)}, 500



def stop_driving():
    a=2
    # po naciśnięciu przycisku stop samochód się zatrzymuje -> dopisujemy czas zatrzymania oraz zmieniamy isDriving na False
    return



###################################################



@app.route("/getCars", methods=["GET"])
def get_cars():
    all_cars = Car.query.all()
    result = cars_schema.dump(all_cars)
    return jsonify(result)


@app.route("/postTrafic", methods=["POST"])
def post_trafic():
    #id = request.json["id"]
    car_id = request.json["car_id"]
    timeofstop = datetime.now()
    sensor_id = request.json["sensor_id"]

    new_trafic = City_Trafic(car_id, timeofstop, sensor_id)
    db.session.add(new_trafic)
    db.session.commit()  # PK increment
    trafic = City_Trafic.query.get(new_trafic.id)
    return car_schema.jsonify(trafic)


@app.route("/stopCar/<id>", methods=["GET","POST"])
def stop_car(id):
    try:
        car = Car.query.get(id)
        if not car:
            return jsonify({"error": f"Car with id {id} not found."}), 404

        car.isDriving = False
        db.session.commit()

        # Znalezienie wpisu w tabeli Server dla danego samochodu bez stopTime
        server_record = Server.query.filter_by(car_id=car.uuid, stopTime=None).first()
        if server_record:
            server_record.stopTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.session.commit()

        # komunikacją z raspberrką o wyłączeniu silników


        return render_template("stop_car.html")
    except Exception as e:
        db.session.rollback()  # Wycofaj zmiany w przypadku błędu
        return jsonify({"error": str(e)}), 500





@app.route("/startCar/<int:id>", methods=["GET","POST"])
def start_car(id):
    car = Car.query.get(id)
    if car:
        car.isDriving = True
        db.session.commit()


        # Dodanie nowego rekordu do tabeli Server
        current_time = datetime.now()
        new_server_record = Server(car_id=car.uuid, city_id=CITY_ID, startTime=current_time, stopTime=None)
        db.session.add(new_server_record)
        db.session.commit()

        return render_template("start_car.html")
    else:
        return jsonify({"error": f"Car with id {id} not found."}), 404


@app.route('/get_car_status', methods=['GET'])
def get_car_status():
    uuid = request.args.get('uuid')  # Pobierz uuid z parametrów URL
    if not uuid:
        return jsonify({"error": "Parameter 'uuid' is required."}), 400

    # Znajdź samochód w bazie danych na podstawie uuid
    car = Car.query.get(4)
    if not car:
        return jsonify({"error": f"Car with uuid '{uuid}' not found."}), 405

    # Utwórz odpowiedź JSON z statusem isDriving
    response = {
        "uuid": car.uuid,
        "isDriving": car.isDriving
    }
    return jsonify(response)


# autorefresh do każdego requesta (?)
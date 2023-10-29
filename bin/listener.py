#!/usr/bin/python

# listens for temperature sensors data published to MQTT Server.

import paho.mqtt.client as mqtt #import the client1
import time
import datetime
import logging
import sqlite3

def logSensorData(recd):
    # attempts to log sensor data from dictionary into database
    # don't bother attempting if we can't connect to the database
    try:
        wcon = sqlite3.connect('/mnt/GigaStore/db/home.db')
    except sqlite3.Error as e:
        logging.error('unable to connect to db on GigaStore')
        logging.error(str(e))
        return

    wcur = wcon.cursor()
    
    if recd is not None:
        # write dictionary to database
        SQL = '''insert into Sensor_Data (ts, loc, val, id) VALUES (:ts, :loc, :val, :id)'''
        wcur.execute(SQL, recd)
        wcon.commit()
        logging.debug('sensor data logged with tag '+recd['ts'])
    else:
        logging.info('No sensor data to log')
    wcon.close()


# define client functions
def on_connect(mqttc, userdata, flags, rc):
    print("Connection returned result: "+str(rc))

def on_disconnect(mqttc, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

def on_message(mqttc, userdata, message):
    # print("message received " ,str(message.payload.decode("utf-8")))
    # convert message into a record dictionary
    msgd = eval(str(message.payload.decode("utf-8")))
    # print (msgd)
    print (msgd['ts']+" | "+msgd['loc']+" | "+str(msgd['val']))
    logSensorData(msgd)
    # print("message topic=",message.topic)
    # print("message qos=",message.qos)
    # print("message retain flag=",message.retain)

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mqttc, obj, level, string):
    logging.debug(string)

broker_address="raspberrypi" # use local MQTT server
ca_certs = "/home/pi/mqtt_srv.crt" # certificate for TLS encryption
subject="sensors"

if __name__ == "__main__":
    logging.basicConfig(filename='/home/pi/logs/listener.log', format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
    logging.debug("starting listener")

    print("creating new instance")
    mqttc = mqtt.Client("P1") #create new instance
    # attach callback functions
    mqttc.on_connect=on_connect
    mqttc.on_disconnect=on_disconnect
    mqttc.on_message=on_message 
    mqttc.on_subscribe=on_subscribe 
    mqttc.on_log=on_log
    mqttc.tls_set(ca_certs,tls_version=2)
    print("connecting to broker")
    mqttc.connect(broker_address, port = 8883) #connect to broker
    print("Subscribing to topic",subject)
    mqttc.subscribe(subject)
    mqttc.loop_forever()

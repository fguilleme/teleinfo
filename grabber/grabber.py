#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = "Sébastien Reuiller"
# __licence__ = "Apache License 2.0"

# Python 3, prerequis : pip install pySerial influxdb
#
# Exemple de trame:
# {
#  'OPTARIF': 'HC..',        # option tarifaire
#  'IMAX': '007',            # intensité max
#  'HCHC': '040177099',      # index heure creuse en Wh
#  'IINST': '005',           # Intensité instantanée en A
#  'PAPP': '01289',          # puissance Apparente, en VA
#  'MOTDETAT': '000000',     # Mot d'état du compteur
#  'HHPHC': 'A',             # Horaire Heures Pleines Heures Creuses
#  'ISOUSC': '45',           # Intensité souscrite en A
#  'ADCO': '000000000000',   # Adresse du compteur
#  'HCHP': '035972694',      # index heure pleine en Wh
#  'PTEC': 'HP..'            # Période tarifaire en cours
# }


import serial
import logging
import logging.handlers
import time
import requests
from datetime import datetime
from influxdb import InfluxDBClient

# clés téléinfo
int_measure_keys = ['BASE', 'IMAX', 'HCHC', 'IINST', 'PAPP', 'ISOUSC', 'ADCO', 'HCHP']

# création du logger
logger = logging.getLogger('teleinfo')
logger.setLevel(logging.INFO)

log_filename='/var/log/teleinfo/releve.log'
# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(
            log_filename, maxBytes=50_000_000, backupCount=5)

formatter = logging.Formatter('%(asctime)s %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

#logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s %(message)s')
logger.info("Teleinfo starting..")

# connexion a la base de données InfluxDB
client = InfluxDBClient('localhost', 8086)
db = "teleinfo2"
connected = False
while not connected:
    try:
        logger.info("Database %s exists?" % db)
        if not {'name': db} in client.get_list_database():
            logger.info("Database %s creation.." % db)
            client.create_database(db)
            logger.info("Database %s created!" % db)
        client.switch_database(db)
        logger.info("Connected to %s!" % db)
    except requests.exceptions.ConnectionError:
        logger.info('InfluxDB is not reachable. Waiting 5 seconds to retry.')
        time.sleep(5)
    else:
        connected = True


def add_measures(measures, time_measure):
    points = []
    for measure, value in measures.items():
        point = {
                    "measurement": 'teleinfo',
                    "tags": {
                        "host": "raspberry",
                        "region": "linky"
                    },
                    "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "fields": {
                        measure: value
                    }
                }
        points.append(point)

    client.write_points(points)


def main():
    with serial.Serial(port='/dev/ttyUSB0', baudrate=1200,
            parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE,
            bytesize=serial.SEVENBITS, timeout=1) as ser:

        logger.info("Teleinfo is reading on /dev/ttyUSB0..")

        trame = dict()

        # boucle pour partir sur un début de trame
        line = ser.readline()
        while b'\x02' not in line:  # recherche du caractère de début de trame
            line = ser.readline()

        # lecture de la première ligne de la première trame
        line = ser.readline()

        while True:
            line_str = line.decode("utf-8")
            logger.info(line_str.strip())
            ar = line_str.split(" ")
            if  len(ar) > 1:
                try:
                    key = ar[0]
                    if key in int_measure_keys :
                        value = int(ar[1])
                    else:
                        value = ar[1]

                    checksum = ar[2]
                    trame[key] = value
                    if b'\x03' in line:  # si caractère de fin dans la ligne, on insère la trame dans influx
                        time_measure = time.time()

                        # insertion dans influxdb
                        add_measures(trame, time_measure)
                        trame = dict()  # on repart sur une nouvelle trame
                except Exception as e:
                    logger.error(line)
                    logger.error("Exception : %s" % e)
            line = ser.readline()


if __name__ == '__main__':
    if connected:
        main()



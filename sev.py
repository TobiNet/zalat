import subprocess
import time
import board
import adafruit_dht
import json
import sys
sys.path.insert(0, './lib_oled96')
from lib_oled96 import ssd1306
from smbus import SMBus
from PIL import ImageFont
from datetime import datetime, timedelta
from influxdb import InfluxDBClient

dhtDevice = adafruit_dht.DHT11(board.D4, use_pulseio=False)

i2cbus = SMBus(1)
oled = ssd1306(i2cbus)
draw = oled.canvas
FreeSans20 = ImageFont.truetype('./lib_oled96/FreeSans.ttf', 20)
FreeSans12 = ImageFont.truetype('./lib_oled96/FreeSans.ttf', 12)


db = InfluxDBClient('localhost', 8086, '', '', 'zalat')
db.create_retention_policy("sensor", 'INF', 3, default=True)

def insertData(temp, humid):
    ts = (datetime.now() - datetime(1970, 1, 1)).total_seconds() 
    now = datetime.utcnow()
    utc = ("Updated", now.strftime("%Y-%m-%dT%H:%M:%SZ"))

    influx = [
            { "measurement": "sensor",
                "tags": { "id": 1},
                "time": utc[1],
                "fields": {
                 "temperature": temp,
                 "humidity": humid,
                 "timestamp": ts
                }
             }
            ]
    db.write_points(influx, retention_policy="sensor")

database_insert = datetime.utcnow() + timedelta(days = -1)
ventilator_triggered = datetime.utcnow() + timedelta(days = -1)
relay = False

while True:
    try:
        # Print the values to the serial port
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity
        print(
            "Temp: {:.1f}°C    Humidity: {}% ".format(
                temperature_c, humidity
            )
        )
        oled.cls()
        draw.text((1, 1), "Zevs Beckzalat", font=FreeSans12, fill=1)
        draw.text((10, 30), "{:.1f}°C {}%".format(temperature_c, humidity), font=FreeSans20, fill=1)
        oled.display()

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        # print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    if (database_insert < (datetime.utcnow() + timedelta(minutes = -30))):
        database_insert = datetime.utcnow()
        insertData(temperature_c, humidity)
        print("DB insert at " + datetime.utcnow().strftime('%H:%M:%S'))

    #if ( temperature_c < 20 ):
    if (relay == False and humidity > 80 and ventilator_triggered < (datetime.utcnow() + timedelta (minutes = -60))):
        subprocess.run(["usbrelay", "/dev/hidraw0_3=1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ventilator_triggered = datetime.utcnow()
        relay = True
        print ("relay on " + ventilator_triggered.strftime('%H:%M:%S'))
    if ( relay == True and ventilator_triggered < (datetime.utcnow() + timedelta (minutes = -20)) ):
        print ("relay off " + datetime.utcnow().strftime('%H:%M:%S'))
        subprocess.run(["usbrelay", "/dev/hidraw0_3=0"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        relay = False

    time.sleep(2.0)


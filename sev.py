import subprocess
import time
import board
import adafruit_dht
import I2C_LCD_driver
import json
import sys
sys.path.insert(0, './lib_oled96')
from lib_oled96 import ssd1306
from smbus import SMBus
from PIL import ImageFont
from datetime import datetime
from influxdb import InfluxDBClient

dhtDevice = adafruit_dht.DHT11(board.D4, use_pulseio=False)
lcd = I2C_LCD_driver.lcd()

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
        lcd.lcd_clear()
        lcd.lcd_display_string("Zevs Becksalat", 1)
        lcd.lcd_display_string("{:.1f} C {}%".format(temperature_c, humidity), 2)
        oled.cls()
        oled.display()
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

    insertData(temperature_c, humidity)

    if ( humidity > 70 ):
        subprocess.run(["usbrelay", "-q", "QAAMZ_3=1"])
    if ( humidity <= 70 ):
        subprocess.run(["usbrelay", "-q", "QAAMZ_3=0"])

    time.sleep(2.0)


import time
import board
import adafruit_dht
import I2C_LCD_driver

import sys
sys.path.insert(0, './lib_oled96')
from lib_oled96 import ssd1306
from smbus import SMBus
from PIL import ImageFont

dhtDevice = adafruit_dht.DHT11(board.D4, use_pulseio=False)
lcd = I2C_LCD_driver.lcd()

i2cbus = SMBus(1)
oled = ssd1306(i2cbus)
draw = oled.canvas
FreeSans20 = ImageFont.truetype('./lib_oled96/FreeSans.ttf', 20)
FreeSans12 = ImageFont.truetype('./lib_oled96/FreeSans.ttf', 12)



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

    time.sleep(2.0)


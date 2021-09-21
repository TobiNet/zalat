import time
import board
import adafruit_dht
import I2C_LCD_driver

dhtDevice = adafruit_dht.DHT11(board.D4, use_pulseio=False)
lcd = I2C_LCD_driver.lcd()

while True:
    try:
        # Print the values to the serial port
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity
        print(
            "Temp: {:.1f} C    Humidity: {}% ".format(
                temperature_c, humidity
            )
        )
        lcd.lcd_clear()
        lcd.lcd_display_string("Zevs Becksalat", 1)
        lcd.lcd_display_string("{:.1f} C {}%".format(temperature_c, humidity), 2)

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        # print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    time.sleep(2.0)


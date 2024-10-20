#
# Code from:
# https://learn.adafruit.com/adafruit-feather-m0-express-designed-for-circuit-python-circuitpython/circuitpython-storage
#
import board
import digitalio
import storage
import neopixel
import time

import array
import math
import audiobusio
from adafruit_apds9960.apds9960 import APDS9960
from adafruit_bmp280 import Adafruit_BMP280_I2C
from adafruit_lis3mdl import LIS3MDL
from adafruit_sht31d import SHT31D


pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)

for i in range(5):
    pixel[0] = (255,255,255) # Warn that we're going to read the switch!
    time.sleep(0.5)
    pixel[0] = (0, 0, 0)
    time.sleep(0.5)
    
#
# We will use the onboard button labeled "User Sw"
#
switch = digitalio.DigitalInOut(board.SWITCH)

#
# Switch will be used for input, and pulled up (+3.3V).
# Pushing the button during reboot will drop the value to GND
#
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

#
# If the switch pin is connected to ground, allow CircuitPython to write to the drive
# (This makes the drive Read-Only for the host computer)
#
i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

# check for LSM6DS33 or LSM6DS3TR-C
try:
    from adafruit_lsm6ds.lsm6ds33 import LSM6DS33 as LSM6DS
    lsm6ds = LSM6DS(i2c)
except RuntimeError:
    from adafruit_lsm6ds.lsm6ds3 import LSM6DS3 as LSM6DS
    lsm6ds = LSM6DS(i2c)

apds9960 = APDS9960(i2c)
bmp280 = Adafruit_BMP280_I2C(i2c)
lis3mdl = LIS3MDL(i2c)
sht31d = SHT31D(i2c)
microphone = audiobusio.PDMIn(board.MICROPHONE_CLOCK, board.MICROPHONE_DATA,
                              sample_rate=16000, bit_depth=16)

def normalized_rms(values):
    minbuf = int(sum(values) / len(values))
    return int(math.sqrt(sum(float(sample - minbuf) *
                             (sample - minbuf) for sample in values) / len(values)))
apds9960.enable_proximity = True
apds9960.enable_color = True

bmp280.sea_level_pressure = 1013.25

storage.remount("/", switch.value)

rows = 1

if switch.value:
    print("/ is Read-Only for Python, Read-Write for host system")
    for i in range(1, 5):
        pixel[0] = (0,255,0)  # Green for Read/Write from Host System
        time.sleep(0.5)
        pixel[0] = (0, 0, 0)
        time.sleep(0.5)
else:
    print("/ is Read-Write for Python, Read-Only for host system")
    for i in range(1, 5):
        pixel[0] = (255,0,0)  # Red for Read/Write from CircuitPython
        time.sleep(0.5)
        pixel[0] = (0, 0, 0)
        time.sleep(0.5)
    f = open('eclipse.csv', 'w')
    f.write('Time, Temprature, Barometric pressure, Red, Green, Blue, Clear, Humidity, Sound level\n')
    while rows < 1000:
        samples = array.array('H', [0] * 160)
        microphone.record(samples, len(samples))
        #values =  + str(bmp280.temperature) + " , " + str(bmp280.pressure) + " , " + str(apds9960.color_data[0]) + " , " +  str(apds9960.color_data[1]) + " , " +  str(apds9960.color_data[2]) + " , " +  str(apds9960.color_data[3]) + " , " +  str(sht31d.relative_humidity) + " , " +  str(normalized_rms(samples)) + "\n" 
        temperature_str = "{:.1f}".format(bmp280.temperature)
        humidity_str = "{:.1f}".format(sht31d.relative_humidity)
        f.write(str(rows) + " , ")
        f.write(temperature_str + " ,")
        f.write(str(bmp280.pressure) + " , ")
        f.write(str(apds9960.color_data[0]) + " , ")
        f.write(str(apds9960.color_data[0]) + " , ")
        f.write(str(apds9960.color_data[0]) + " , ")
        f.write(str(apds9960.color_data[0]) + " , ")
        f.write(str(humidity_str) + " , ")
        f.write(str(normalized_rms(samples)) + "\n ")
        time.sleep(0.6)
        rows += 1
    f.close()
 
 



# *****************************************************************************
# * | File        :	  epdconfig.py
# * | Author      :   Waveshare team
# * | Function    :   Hardware underlying interface
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2024-04-08
# # | Info        :   python demo
# *****************************************************************************
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os
import logging
import sys
import time

logger = logging.getLogger(__name__)

class RaspberryPi:
    # Pin definition
    RST_PIN         = 17
    DC_PIN          = 25
    CS_PIN          = 8
    BUSY_PIN        = 24

    def __init__(self):
        import spidev
        import RPi.GPIO

        self.GPIO = RPi.GPIO
        self.SPI = spidev.SpiDev()

    def digital_write(self, pin, value):
        self.GPIO.output(pin, value)

    def digital_read(self, pin):
        return self.GPIO.input(pin)

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.SPI.writebytes(data)

    def spi_writebyte2(self, data):
        self.SPI.writebytes2(data)

    def module_init(self):
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setwarnings(False)
        self.GPIO.setup(self.RST_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.DC_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.CS_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.BUSY_PIN, self.GPIO.IN)

        # SPI device, bus = 0, device = 0
        self.SPI.open(0, 0)
        self.SPI.max_speed_hz = 4000000
        self.SPI.mode = 0b00
        return 0

    def module_exit(self, cleanup=False):
        logger.debug("spi end")
        self.SPI.close()

        logger.debug("close 5V, Module enters 0 power consumption ...")
        if cleanup:
            self.GPIO.cleanup([self.RST_PIN, self.DC_PIN, self.CS_PIN, self.BUSY_PIN])
        return 0

# For Jetson Nano
class JetsonNano:
    # Pin definition
    RST_PIN         = 17
    DC_PIN          = 25
    CS_PIN          = 8
    BUSY_PIN        = 24

    def __init__(self):
        import ctypes
        find_dirs = [
            os.path.dirname(os.path.realpath(__file__)),
            '/usr/local/lib',
            '/usr/lib',
        ]
        self.SPI = None
        for find_dir in find_dirs:
            so_filename = os.path.join(find_dir, 'sysfs_software_spi.so')
            if os.path.exists(so_filename):
                self.SPI = ctypes.cdll.LoadLibrary(so_filename)
                break
        if self.SPI is None:
            raise RuntimeError('Cannot find sysfs_software_spi.so')

        import Jetson.GPIO
        self.GPIO = Jetson.GPIO

    def digital_write(self, pin, value):
        self.GPIO.output(pin, value)

    def digital_read(self, pin):
        return self.GPIO.input(self.BUSY_PIN)

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.SPI.SYSFS_software_spi_transfer(data[0])

    def spi_writebyte2(self, data):
        for i in range(len(data)):
            self.SPI.SYSFS_software_spi_transfer(data[i])

    def module_init(self):
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setwarnings(False)
        self.GPIO.setup(self.RST_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.DC_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.CS_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.BUSY_PIN, self.GPIO.IN)
        self.SPI.SYSFS_software_spi_begin()
        return 0

    def module_exit(self, cleanup=False):
        logger.debug("spi end")
        self.SPI.SYSFS_software_spi_end()

        logger.debug("close 5V, Module enters 0 power consumption ...")
        if cleanup:
            self.GPIO.cleanup([self.RST_PIN, self.DC_PIN, self.CS_PIN, self.BUSY_PIN])
        return 0

class SunriseX3:
    # Pin definition
    RST_PIN         = 17
    DC_PIN          = 25
    CS_PIN          = 8
    BUSY_PIN        = 24

    def __init__(self):
        import hobot.gpio as gpio
        import spidev
        self.GPIO = gpio
        self.SPI = spidev.SpiDev()

    def digital_write(self, pin, value):
        self.GPIO.output(pin, value)

    def digital_read(self, pin):
        return self.GPIO.input(pin)

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.SPI.writebytes(data)

    def spi_writebyte2(self, data):
        self.SPI.writebytes2(data)

    def module_init(self):
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setwarnings(False)
        self.GPIO.setup(self.RST_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.DC_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.CS_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.BUSY_PIN, self.GPIO.IN)

        # SPI device, bus = 0, device = 0
        self.SPI.open(1, 0)
        self.SPI.max_speed_hz = 4000000
        self.SPI.mode = 0b00
        return 0

    def module_exit(self, cleanup=False):
        logger.debug("spi end")
        self.SPI.close()

        logger.debug("close 5V, Module enters 0 power consumption ...")
        if cleanup:
            self.GPIO.cleanup([self.RST_PIN, self.DC_PIN, self.CS_PIN, self.BUSY_PIN])
        return 0

class ESP32:
    # Pin definition
    RST_PIN         = 16
    DC_PIN          = 17
    CS_PIN          = 5
    BUSY_PIN        = 4

    def __init__(self):
        import machine
        import spidev
        self.GPIO = machine
        self.SPI = machine.SPI(1, 10000000, sck=machine.Pin(18), mosi=machine.Pin(23))

    def digital_write(self, pin, value):
        if pin == self.RST_PIN:
            self.rst.value(value)
        elif pin == self.DC_PIN:
            self.dc.value(value)
        elif pin == self.CS_PIN:
            self.cs.value(value)
            
    def digital_read(self, pin):
        if pin == self.BUSY_PIN:
            return self.busy.value()
            
    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)
        
    def spi_writebyte(self, data):
        self.SPI.write(bytearray(data))
        
    def spi_writebyte2(self, data):
        self.SPI.write(bytearray(data))
        
    def module_init(self):
        self.rst = self.GPIO.Pin(self.RST_PIN, self.GPIO.OUT, value=1)
        self.dc = self.GPIO.Pin(self.DC_PIN, self.GPIO.OUT, value=0)
        self.busy = self.GPIO.Pin(self.BUSY_PIN, self.GPIO.IN)
        self.cs = self.GPIO.Pin(self.CS_PIN, self.GPIO.OUT, value=1)
        
        return 0
        
    def module_exit(self, cleanup=False):
        logger.debug("spi end")
        if cleanup:
            self.GPIO.Pin(self.RST_PIN, self.GPIO.IN)
            self.GPIO.Pin(self.DC_PIN, self.GPIO.IN)
            self.GPIO.Pin(self.CS_PIN, self.GPIO.IN)
            self.GPIO.Pin(self.BUSY_PIN, self.GPIO.IN)

# Select the hardware platform
if os.path.exists('/sys/bus/platform/drivers/gpiomem-bcm2835'):
    implementation = RaspberryPi()
elif os.path.exists('/sys/bus/platform/drivers/gpio-x3'):
    implementation = SunriseX3()
elif os.path.exists('/sys/firmware/devicetree/base/model'):
    with open('/sys/firmware/devicetree/base/model', 'r') as file:
        model = file.read()
        if 'Jetson' in model:
            implementation = JetsonNano()
        elif 'Raspberry' in model:
            implementation = RaspberryPi()
        else:
            implementation = RaspberryPi()
else:
    try:
        import platform
        if platform.node() == 'esp32':
            implementation = ESP32()
        else:
            implementation = RaspberryPi()
    except:
        implementation = RaspberryPi()

# Expose the implementation to users
digital_write = implementation.digital_write
digital_read = implementation.digital_read
delay_ms = implementation.delay_ms
spi_writebyte = implementation.spi_writebyte
spi_writebyte2 = implementation.spi_writebyte2
module_init = implementation.module_init
module_exit = implementation.module_exit

RST_PIN = implementation.RST_PIN
DC_PIN = implementation.DC_PIN
CS_PIN = implementation.CS_PIN
BUSY_PIN = implementation.BUSY_PIN

### END OF FILE ### 
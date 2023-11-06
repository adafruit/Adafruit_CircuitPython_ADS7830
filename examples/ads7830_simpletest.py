# SPDX-FileCopyrightText: 2023 Liz Clark for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple demo to read 8 analog inputs
# from ADS7830 ADC

import time
import board
import adafruit_ads7830

i2c = board.I2C()

# Initialize ADS7830
adc = adafruit_ads7830.Adafruit_ADS7830(i2c)

while True:
    for i in range(8):
        print(f"ADC channel {i} = {adc.value[i]}")
    time.sleep(0.1)

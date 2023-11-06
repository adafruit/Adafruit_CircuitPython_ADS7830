# SPDX-FileCopyrightText: Copyright (c) 2023 Liz Clark for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_ads7830`
================================================================================

CircuitPython driver for the ADS7830 analog to digital converter


* Author(s): Liz Clark

Implementation Notes
--------------------

**Hardware:**

* `Adafruit ADS7830 8-Channel 8-Bit ADC with I2C <https://www.adafruit.com/product/5836>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
"""

from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const

try:
    import typing  # pylint: disable=unused-import
    from busio import I2C
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_ADS7830.git"

_I2C_ADDR = const(0x48)


class Adafruit_ADS7830:
    """Adafruit ADS7830 ADC driver"""

    # Power-down modes
    _POWER_DOWN_MODES = [
        0x00,  # POWER_DOWN_BETWEEN_CONVERSIONS
        0x01,  # INTERNAL_REF_OFF_ADC_ON
        0x02,  # INTERNAL_REF_ON_ADC_OFF
        0x03,  # INTERNAL_REF_ON_ADC_ON (default)
    ]
    # Single channel selection list
    _CHANNEL_SELECTION = [
        0x08,  # SINGLE_CH0
        0x0C,  # SINGLE_CH1
        0x09,  # SINGLE_CH2
        0x0D,  # SINGLE_CH3
        0x0A,  # SINGLE_CH4
        0x0E,  # SINGLE_CH5
        0x0B,  # SINGLE_CH6
        0x0F,  # SINGLE_CH7
    ]
    # Differential channel selection list
    _DIFF_CHANNEL_SELECTION = [
        0x00,  # DIFF_CH0_CH1
        0x04,  # DIFF_CH1_CH0
        0x01,  # DIFF_CH2_CH3
        0x05,  # DIFF_CH3_CH2
        0x02,  # DIFF_CH4_CH5
        0x06,  # DIFF_CH5_CH4
        0x03,  # DIFF_CH6_CH7
        0x07,  # DIFF_CH7_CH6
    ]

    def __init__(self, i2c: I2C, address: int = _I2C_ADDR) -> None:
        self.i2c_device = I2CDevice(i2c, address)

    def _single_channel(self, channel: int, pd_mode: int = 3) -> int:
        """ADC value in single-ended mode
        Scales the 8-bit ADC value to a 16-bit value

        :param int channel: Channel (0-7)
        :param int pd_mode: Power-down mode
        :return: Scaled ADC value or raise an exception if read failed
        :rtype: int
        """
        if channel > 7:
            raise ValueError("Invalid channel: must be 0-7")

        command_byte = self._CHANNEL_SELECTION[channel]
        command_byte <<= 4
        command_byte |= self._POWER_DOWN_MODES[pd_mode] << 2

        with self.i2c_device as i2c:
            try:
                # Buffer to store the read ADC value
                adc_value = bytearray(1)
                i2c.write_then_readinto(bytearray([command_byte]), adc_value)
                # Scale the 8-bit value to 16-bit
                return adc_value[0] << 8
            except Exception as error:
                raise RuntimeError(f"Failed to read value: {error}") from error

    def _differential_channel(self, channel: int, pd_mode: int = 3) -> int:
        """ADC value in differential mode
        Scales the 8-bit ADC value to a 16-bit value

        :param int channel: Positive channel for differential reading (0-7)
        :param int pd_mode: Power-down mode
        :return: Scaled ADC value or raise an exception if read failed
        :rtype: int
        """
        if channel > 7:
            raise ValueError("Invalid channel: must be 0-7")

        command_byte = self._DIFF_CHANNEL_SELECTION[channel // 2]
        command_byte <<= 4
        command_byte |= self._POWER_DOWN_MODES[pd_mode] << 2

        with self.i2c_device as i2c:
            try:
                # Buffer to store the read ADC value
                adc_value = bytearray(1)
                i2c.write_then_readinto(bytearray([command_byte]), adc_value)
                # Scale the 8-bit value to 16-bit
                return adc_value[0] << 8
            except Exception as error:
                raise RuntimeError(f"Failed to read value: {error}") from error

    @property
    def value(self) -> typing.List[int]:
        """Single-ended mode ADC values for all channels

        :rtype: List[int]"""
        values = []
        for i in range(8):
            single_value = self._single_channel(i)
            values.append(single_value)
        return values

    @property
    def differential_value(self) -> typing.List[int]:
        """Differential ADC values for all channel pairs

        :rtype: List[int]"""
        values = []
        for i in range(0, 8, 2):  # Iterate over channel pairs
            diff_value = self._differential_channel(i)
            values.append(diff_value)
        return values

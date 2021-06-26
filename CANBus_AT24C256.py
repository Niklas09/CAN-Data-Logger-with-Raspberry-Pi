#!/usr/bin/python3

# zum Schreiben in bzw. Lesen vom externen EEPROM AT24C256
#
# HINWEIS: - unter C bzw. C++ mit einem Microcontroller erfolgt das Lesen und Schreiben mit mit der Adresse 0xA1 (Read) bzw. 0xA0 (Write)
#          - speziell auf dem RPi (unter Python) erfolgt das Lesen und Schreiben mit der Adresse 0x50

import smbus
import time


def Write_EEPROM(address_2, value, bus, slave, address_1):
    # -> es findet ein byte-weise Schreiben statt!

    values=[address_2, value]

    bus.write_i2c_block_data(slave, address_1, values)


def Read_EEPROM(address_2, bus, slave, address_1):
    # -> es findet ein byte-weise Lesen statt!

    values=[address_2]

    bus.write_i2c_block_data(slave, address_1, values)
    time.sleep(0.01)

    data=bus.read_byte(slave)

    return data



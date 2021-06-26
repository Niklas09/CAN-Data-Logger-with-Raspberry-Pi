#!/usr/bin/python3

import smbus
import time


def zehntel(variable):
    if(variable==0x00):
        var=0
    elif(variable==0x01):
        var=1
    elif(variable==0x02):
        var=2
    elif(variable==0x03):
        var=3
    elif(variable==0x04):
        var=4
    elif(variable==0x05):
        var=5
    elif(variable==0x06):
        var=6
    elif(variable==0x07):
        var=7
    elif(variable==0x08):
        var=8
    elif(variable==0x09):
        var=9

    return var


def hunderstel(variable):
    if(variable==0x00):
        var=0
    elif(variable==0x10):
        var=1
    elif(variable==0x20):
        var=2
    elif(variable==0x30):
        var=3
    elif(variable==0x40):
        var=4
    elif(variable==0x50):
        var=5
    elif(variable==0x60):
        var=6
    elif(variable==0x70):
        var=7

    return var


def zehntel_hex(variable):
    if(variable==0):
        var=0x00
    elif(variable==1):
        var=0x01
    elif(variable==2):
        var=0x02
    elif(variable==3):
        var=0x03
    elif(variable==4):
        var=0x04
    elif(variable==5):
        var=0x05
    elif(variable==6):
        var=0x06
    elif(variable==7):
        var=0x07
    elif(variable==8):
        var=0x08
    elif(variable==9):
        var=0x09
    return var


def hunderstel_hex(variable):
    if(variable==0):
        var=0x00
    elif(variable==1):
        var=0x10
    elif(variable==2):
        var=0x20
    elif(variable==3):
        var=0x30
    elif(variable==4):
        var=0x40
    elif(variable==5):
        var=0x50
    elif(variable==6):
        var=0x60
    elif(variable==7):
        var=0x70
    elif(variable==8):
        var=0x80
    elif(variable==9):
        var=0x90

    return var


def Read_Seconds(bus, slave):
    bus.write_byte(slave, 0x00)
    seconds=bus.read_byte(slave)

    # -> Umwandlung
    sec_a=seconds&0x0F
    sec_b=seconds&0xF0
    second_1=zehntel(sec_a)
    second_10=hunderstel(sec_b)

    sekunden=[second_10, second_1]

    return sekunden


def Read_Minutes(bus, slave):
    bus.write_byte(slave, 0x01)
    minutes=bus.read_byte(slave)

    # -> Umwandlung
    minute_a=minutes&0x0F
    minute_b=minutes&0xF0
    minute_1=zehntel(minute_a)
    minute_10=hunderstel(minute_b)

    minuten=[minute_10, minute_1]

    return minuten


def Read_Hours(bus, slave):
    bus.write_byte(slave, 0x02)
    hours=bus.read_byte(slave)

    # -> Umwandlung
    hour_a=hours&0x0F
    hour_b=hours&0x10
    hour_c=hours&0x20
    hour_1=zehntel(hour_a)

    # ---> wenn Bit 4 low, dann 0Uhr...9Uhr; sonst 10Uhr...19Uhr
    if(hour_b==0x00):
        hour_10=0
    elif(hour_b==0x10):
        hour_10=1

    # ---> wenn Bit 5 high, dann 20Uhr...23Uhr
    if(hour_c==0x20):
        hour_20=2
    elif(hour_c==0x00):
        hour_20=0
    
    # ---> tatsaechlich hunderstel Stunde
    if(hour_10==1):
        if(hour_20==0):
            hour_hunderstel=1
        else:
            hour_hunderstel=0
    elif(hour_10==0):
        if(hour_20==2):
            hour_hunderstel=2
        else:
            hour_hunderstel=0

    stunden=[hour_hunderstel, hour_1]

    return stunden


def Read_Date(bus, slave):
    bus.write_byte(slave, 0x04)
    date=bus.read_byte(slave)

    # -> Umwandlung
    date_a=date&0x0F
    date_b=date&0xF0
    date_1=zehntel(date_a)
    date_10=hunderstel(date_b)

    tag=[date_10, date_1]

    return tag


def Read_Month(bus, slave):
    bus.write_byte(slave, 0x05)
    month=bus.read_byte(slave)

    # -> Umwandlung
    month_a=month&0x0F
    month_b=month&0x10
    month_1=zehntel(month_a)

    # ---> wenn Bit 4 high, dann 10...12; sonst 1...9
    if(month_b==0x00):
        month_10=0
    elif(month_b==0x10):
        month_10=1

    monat=[month_10, month_1]

    return monat


def Read_Year(bus, slave):
    bus.write_byte(slave, 0x06)
    year=bus.read_byte(slave)

    # -> Umwandlung
    year_a=year&0x0F
    year_b=year&0xF0
    year_1=zehntel(year_a)
    year_10=hunderstel(year_b)

    jahr=[year_10, year_1]

    return jahr


def Write_Seconds(zehn_tel, hundert_tel, bus, slave):
    sec_1=zehntel_hex(zehntel_tel)
    sec_10=hunderstel_hex(hundert_tel)
    value=sec_10|sec_1
    values=[value]
    # -> beim Schreiben ins Register muss die Funktion write_i2c_block_data() verwendet werden!
    bus.write_i2c_block_data(slave, 0x00, values)


def Write_Minutes(zehn_tel, hundert_tel, bus, slave):
    minute_1=zehntel_hex(zehn_tel)
    minute_10=hunderstel_hex(hundert_tel)
    value=minute_10|minute_1
    values=[value]
    # -> beim Schreiben ins Register muss die Funktion write_i2c_block_data() verwendet werden!
    bus.write_i2c_block_data(slave, 0x01, values)


def Write_Hours(zehn_tel, hundert_tel, bus, slave):
    hour_1=zehntel_hex(zehn_tel)
    hour_10=hunderstel_hex(hundert_tel)
    value=hour_10|hour_1
    values=[value]
    # -> beim Schreiben ins Register muss die Funktion write_i2c_block_data() verwendet werden!
    bus.write_i2c_block_data(slave, 0x02, values)


def Write_Day(zehn_tel, hundert_tel, bus, slave):
    date_1=zehntel_hex(zehn_tel)
    date_10=hunderstel_hex(hundert_tel)
    value=date_10|date_1
    values=[value]
    # -> beim Schreiben ins Register muss die Funktion write_i2c_block_data() verwendet werden!
    bus.write_i2c_block_data(slave, 0x04, values)


def Write_Month(zehn_tel, hundert_tel, bus, slave):
    month_1=zehntel_hex(zehn_tel)
    month_10=hunderstel_hex(hundert_tel)
    value=month_10|month_1
    values=[value]
    # -> beim Schreiben ins Register muss die Funktion write_i2c_block_data() verwendet werden!
    bus.write_i2c_block_data(slave, 0x05, values)


def Write_Year(zehn_tel, hundert_tel, bus, slave):
    year_1=zehntel_hex(zehn_tel)
    year_10=hunderstel_hex(hundert_tel)
    value=year_10|year_1
    values=[value]
    # -> beim Schreiben ins Register muss die Funktion write_i2c_block_data() verwendet werden!
    bus.write_i2c_block_data(slave, 0x06, values)



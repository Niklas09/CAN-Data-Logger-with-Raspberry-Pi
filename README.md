# CAN-Data-Logger-with-Raspberry-Pi
Data logging of every car with Raspberry Pi

It is a data logger for the CAN Bus of a car. It is based on a Raspberry Pi and PiCAN2. The aim of this project is to log measurements like revolution speed and cooling temperature of every car.
It is doing with Raspberry Pi 1 B+ and the OS Arch Linux. 
At the beginning following lines have to be add in /boot/config.txt:

	dtparam=spi=on
	dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=25
	dtoverlay=spi-bcm2835-overlay

The Raspberry Pi is connecting with OBD2 of the car for the data and with USB of the car for power. 
The programm is running with following command:

	python3 CANBus_Datenlogger_Autowahl+LCD.py 
	
Following libraries have to be installed: RPi.GPIO, can, queue, subprocess, numpy, matplotlib.pyplot, smbus
Following files are installed with the standard python package: time, datetime, os, csv 

The files CANBus_Datenlogger_Autowahl+LCD.py, CANBus_PIDs.py, CANBus_SIDs.py, CANBus_LCD.py, CANBus_AT24C256.py and CANBus_DS3231.py should be in a common directory.

The following file can be used to read the Vehicle Identification Number (VIN) and the errors:

	python3 CANBus_Fehlerspeicher-lesen.py

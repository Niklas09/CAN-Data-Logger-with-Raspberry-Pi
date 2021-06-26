#!/usr/bin/python3
#
# HINWEIS: Es werden zuerst Messwerte ueber den CANBus geholt und dann in eine csv-Datei geschrieben
#          (Es geschieht nacheinander, nicht gleichzeitig!)

import RPi.GPIO as GPIO
import can
import time
import datetime
import queue
import os
import subprocess
import numpy
import matplotlib.pyplot as plt
import csv
import smbus
import CANBus_PIDs
import CANBus_SIDs
import CANBus_LCD
import CANBus_DS3231
import CANBus_AT24C256


def Datum():
    aktuelles_Datum=datetime.date.today()
    aktuelles_Datum=str(aktuelles_Datum.day)+'-'+str(aktuelles_Datum.month)+'-'+str(aktuelles_Datum.year)

    return aktuelles_Datum


def Uhrzeit():
    zeit=time.asctime()
    zeit=str(zeit)
    zeit=zeit[11:19]
    zeit=zeit[:2]+'-'+zeit[3:5]+'-'+zeit[6:]

    return zeit


def AktuelleZeit_RTC(bus_1, slave_rtc, slave_lcd):
    secs=CANBus_DS3231.Read_Seconds(bus_1, slave_rtc)
    minutes=CANBus_DS3231.Read_Minutes(bus_1, slave_rtc)
    hours=CANBus_DS3231.Read_Hours(bus_1, slave_rtc)
    days=CANBus_DS3231.Read_Date(bus_1, slave_rtc)
    months=CANBus_DS3231.Read_Month(bus_1, slave_rtc)
    years=CANBus_DS3231.Read_Year(bus_1, slave_rtc)

    datum=str(days[0])+str(days[1])+'-'+str(months[0])+str(months[1])+'-'+str(years[0])+str(years[1])
    uhrzeit=str(hours[0])+str(hours[1])+':'+str(minutes[0])+str(minutes[1])+':'+str(secs[0])+str(secs[1])

    CANBus_LCD.Write_Time(bus_1, slave_lcd, datum, uhrzeit)


def CANBus_transmit(bus_1, request, extID, pid):
    # -> als CAN-Bus-Botschaft wird ein (Standard) Data-Frame zum Abfragen von Messwerten gesendet
    # -> der DLC (= Data Length Code) ist 8, also 8 Byte Nutzdaten
    # -> in der Liste data sind die 8 Byte Nutzdaten
    # -> arbitration_id ist der Indentifier des Arbitration Field (das Arbitration Field besteht aus dem Identifier und dem RTR)
    # -> bei is_extended_id=0 handelt es sich um einen 11-Bit-Identifier; bei is_extended_id=1 handelt es sich um einen 29-Bit-Identifier
    #    (bei is_extended_id=1 wird ein X angezeigt; bei is_extended_id=0 wird ein S angezeigt)
    # -> es koennen auch die Frametypen is_error_frame und is_remote_frame angegeben werden
    #    (bei is_error_frame=1 wird ein E angezeigt; bei is_remote_frame=1 wird ein R angezeigt)
    # -> bei is_remote_frame=1 wird angegeben, dass es sich um ein Remote-Frame handelt; bei is_remote_frame=0 handelt es sich um eine Daten-Frame
    # -> bei is_error_frame=1 wird angegeben, dass es sich um ein Error-Frame handelt; bei is_error_frame=0 handelt es sich nicht um ein Error-Frame
    # -> bei is_fd=0 wird angegeben, dass es sich um den normalen CAN handelt; bei is_fd=1 handelt es sich um den neuen CAN FD
    #    (fuer den neuen CAN FD sind die Variablen bitrate_switch und error_state_inidcator interessant; beide sind bool-Werte)
    message=can.Message(arbitration_id=request, is_extended_id=extID,  is_remote_frame=False, is_error_frame=False, data=[0x02,CANBus_SIDs.SID1,pid,0x00,0x00,0x00,0x00,0x00], is_fd=False, bitrate_switch=False, error_state_indicator=False, extended_id=extID)
    bus_1.send(message)
    time.sleep(0.05)


def CANBus_receive(bus_1, timeout):
    msg=bus_1.recv(timeout)

    return msg


def CAN_Botschaft(bus_1, request, ext_ID, pid_xxx, i, file, i_output, queue_1):
    # -> Anfrage fuer eine bestimmte CAN-Bus-Botschaft stellen
    CANBus_transmit(bus_1, request, ext_ID, pid_xxx)
    #print('CAN-Bus-Botschaft ist gesendet.')

    # -> Antwirt zur gestellten Anfrage bekommen
    message=CANBus_receive(bus_1, 100)

    if message is None:
        print('Timeout erreicht, keine CAN-Bus-Botschaft.')
    else:
        way='Rx'

        if(pid_xxx==0x05):
            value=message.data[3]-40
            file.write(str(i)+';Kuehlmitteltemperatur:;'+str(value)+';*C'+'\n')
            print(Ausgabe_String(message, i_output, way)+' => '+'Kuehlmitteltemperatur: '+str(value)+' *C')
            queue_1.put(int(value))
        elif(pid_xxx==0x0C):
            value=((message.data[3]*256)+message.data[4])/4
            file.write(str(i)+';Drehzahl:;'+str(value)+';rpm'+'\n')
            print(Ausgabe_String(message, i_output, way)+' => '+'Drehzahl: '+str(value)+' rpm')
            queue_1.put(int(value))
        elif(pid_xxx==0x11):
            value=(message.data[3]*100)/255
            file.write(str(i)+';Absolute Gaspedalstellung:;'+str(value)+';%'+'\n')
            print(Ausgabe_String(message, i_output, way)+' '+'Absolute TROTTLE: '+str(value)+' %')
        elif(pid_xxx==0x0D):
            value=message.data[3]
            file.write(str(i)+';Fahrgeschwindigkeit:;'+str(value)+';km/h'+'\n')
            print(Ausgabe_String(message, i_output, way)+' => '+'Fahrgeschwindigkeit: '+str(value)+' km/h')
        elif(pid_xxx==0x1F):
            value=(message.data[3]*256)+message.data[4]
            file.write(str(i)+';Motorlaufzeit:;'+str(value)+';sec.'+'\n')
            print(Ausgabe_String(message, i_output, way)+' => '+'Motorlaufzeit: '+str(value)+' sec.')
        elif(pid_xxx==0x45):
            value=(100/255)*message.data[3]
            file.write(str(i)+';Relative Gaspedalstellung:;'+str(value)+';%'+'\n')
            print(Ausgabe_String(message, i_output, way)+' => '+'Relative THROTTLE: '+str(value)+' %')
            #queue_1.put(int(value))
            values=Convert_FloatNumber(value)
            queue_1.put(values[0])
            queue_1.put(values[1])
        elif(pid_xxx==0x46):
            value=message.data[3]-40
            file.write(str(i)+';Umgebungstemperatur:;'+str(value)+';*C'+'\n')
            print(Ausgabe_String(message, i_output, way)+' => '+'Umgebungstemperatur: '+str(value)+' *C')
        # HINWEIS: bei den einen Fahrzeugen funktioniert die PID 0x10, bei den anderen Fahrzeugen funktioniert die PID 0x66 
        elif(pid_xxx==0x10):
            value=(256*message.data[3]+message.data[4])/100
            file.write(str(i)+';MAF-Sensor:;'+str(value)+';g/s'+'\n')
            print(Ausgabe_String(message, i_output, way)+' => '+'MAF-Sensor: '+str(value)+' g/s = '+str((value*3600))+' kg/h => aktuelle Leistung: '+str((value*1.08))+' PS')
        elif(pid_xxx==0x66):
            value=(256*message.data[3]+message.data[4])/100
            file.write(str(i)+';MAF-Sensor:;'+str(value)+'g/s'+'\n')
            print(Ausgabe_String(message, i_output, way)+' => '+'MAF-Sensor: '+str(value)+' g/s = '+str((value*3600))+' kg/h => aktuelle Leistung: '+str((value*1.08))+' PS')
        elif(pid_xxx==0x33):
            value=(message.data[3]*1000)/100000
            file.write(str(i)+';Umgebungsdruck:;'+str(value)+';bar'+'\n')
            print(Ausgabe_String(message, i_output, way)+' => '+'Umgebungsdruck: '+str(value)+' bar')
        elif(pid_xxx==0x04):
            value=(100/255)*message.data[3]
            file.write(str(i)+';Motorlast:;'+str(value)+';%'+'\n')
            print(Ausgabe_String(message, i_output, way)+' => '+'Motorlast: '+str(value)+' %')
            #queue_1.put(int(value))
            values=Convert_FloatNumber(value)
            queue_1.put(values[0])
            queue_1.put(values[1])
        elif(pid_xxx==0x0E):
            value=(message.data[3]/2)-64
            file.write(str(i)+';Totpunkt:;'+str(value)+';*'+'\n')
            print(Ausgabe_String(message, i_output, way)+' => '+'Totpunkt: '+str(value)+' *')
        elif(pid_xxx==0x15):
            value_v=message.data[3]/200
            value_prozent=((100/128)*message.data[4])-100
            file.write(str(i)+';Lambdawert:;'+str(value_prozent)+';1'+'\n')
            print(Ausgabe_String(message, i_output, way)+' => '+'Spannung der Lambdasonde: '+str(value_v)+' V und Lambdawert: '+str(value_prozent)+' %')
        elif(pid_xxx==0x06):
            value=((100/128)*message.data[3])-100
            file.write(str(i)+';Short Term Fuel Trim - Bank 1 (=SFT):;'+str(value)+';%'+'\n')
            print(Ausgabe_String(message, i_output, way)+' => '+'Short Term Fuel Trim - Bank 1 (=SFT): '+str(value)+' %')
        elif(pid_xxx==0x07):
            value=((100/128)*message.data[3])-100
            file.write(str(i)+';Long Term Fuel Trim - Bank 1 (=LFT):;'+str(value)+';%'+'\n')
            print(Ausgabe_String(message, i_output, way)+' => '+'Long Term Fuel Trim - Bank 1 (=LFT): '+str(value)+' %')

        #print('CAN-Bus-Botschaft empfangen.')


def CAN_Botschaft_withQueue(bus_1, request, ext_ID, pid_xxx, queue_1):
    # -> Anfrage stellen
    CANBus_transmit(bus_1, request, ext_ID, pid_xxx)
    print('CAN-Bus-Botschaft gesendet.')

    # -> Antwort auf die gestellte Anfrage bekommen
    message=CANBus_receive(bus_1, 100)

    if message is None:
        print('Timeout erreicht, keine CAN-Bus-Botschaft.')
    else:
        # -> Fuellstand Tank
        if(pid_xxx==0x2F):
            value=(100/255)*message.data[3]
        # -> zurueckgelegte Strecke
        elif(pid_xxx==0x31):
            value=256*message.data[3]+message.data[4]

        queue_1.put(value)


def Ausgabe():
    print('Channel  Counter Tx/Rx  Timestamp    ID  DLC Data    Description')


def Ausgabe_String(msg, counter, direction):
    text=str(msg.channel)+' '+str(counter)+'    '+direction+'  '+str(msg.timestamp)+'   '+str(hex(msg.arbitration_id))+'   '+str(msg.dlc)+'  '+str(hex(msg.data[0]))+'    '+str(hex(msg.data[1]))+'    '+str(hex(msg.data[2]))+'    '+str(hex(msg.data[3]))+'    '+str(hex(msg.data[4]))+'    '+str(hex(msg.data[5]))+'    '+str(hex(msg.data[6]))+'    '+str(hex(msg.data[7]))

    return text


def Convert_FloatNumber(value):
    value=round(value, 1)
    value_int_1=int(value)
    value_float=value-value_int_1
    value_int_2=value_float*1000
    value_int_2=int(value_int_2)

    # -> es soll nur tatsaechlich eine Nachkommastelle erscheinen
    value_str_2=str(value_int_2)
    value_str_2=value_str_2[:1]
    value_int_2=int(value_str_2)

    value_float_final=[value_int_1, value_int_2]
    #value_float_final=str(value_int_1)+'.'+str(value_int_2)

    return value_float_final




### Start 'Definitionen' ###
BUILTINLED=22
EXTERNALLED=21

count=1
count_output=1
command_interface='cat /sys/class/net/can0/operstate'

nr_x=[]
kuehlmitteltemperatur_y=[]
drehzahl_y=[]
fahrgeschwindigkeit_y=[]
throttle_absolute_y=[]
motorlaufzeit_y=[]
throttle_relative_y=[]
umgebungstemperatur_y=[]
umgebungsdruck_y=[]
motorlast_y=[]
totpunkt_y=[]
oxygen_y=[]
sft_y=[]
lft_y=[]
directory='/home/niklas/eigene_Programme_niklas/CANBus/Diagrams/'

# -> PIDs (= Parameter IDs) zum Anfragen, welche Daten man vom Auto haben will
#    (es wird zuerst eine PID auf den CAN-Bus des Autos als Anfrage gesendet, um dann zu dieser Anfrage Messwerte zu erhalten)
# ---> diese liegen in der Datei 'CANBus_PIDs.py'!

# die Pin-Nummerierung des Broadcom-Chips verwenden
GPIO.setmode(GPIO.BCM)

# Fehlermeldungen bzgl. der GPIO-Pins ignorieren
GPIO.setwarnings(False)

# GPIO-Pin-Definition
GPIO.setup(BUILTINLED, GPIO.OUT)
GPIO.setup(EXTERNALLED, GPIO.OUT)

# pruefen, ob die CAN-Bus-Schnittxtelle can0 an ist
# (die Funktion os.system() liefert keinen Rueckgabewert im Vergleich zu subprocess.check_output)
can0_state=subprocess.check_output(command_interface, shell=True)

if(can0_state==b'down\n'):
    # (die meisten CAN-Bus-Netze im Auto haben eine Baudrate von 500000 = 500 kBit/s [CAN-High-Speed])
    os.system('/sbin/ip link set can0 up type can bitrate 500000')
    print('can0 eingeschalten.')
else:
    print('can0 ist schon an.')


# CAN-Bus-Schnittstelle can0 festlegen
canbus_1=can.interface.Bus(channel='can0', bustype='socketcan_native')
#canbus_1=can.interface.Bus(channel='can0', bustype='socketcan_ctypes')


# Queues definieren
# (es wird die Bibliothek 'queue' gebraucht)
# -> die Queue arbeitet nach dem Prinzip FIFO (es ist ein Stapelspeicher)
#    (mit der Bibliothek asyncio.LifoQueue kann auch eine Queue nach dem Prinzip LIFO erstellt werden: queue_messages=asyncio.LifoQueue() )
# ---> mit queue_messages.Queue(maxsize=5) kann die max. Groesse der Queue auf 5 Elemente begrenzt werden
# ---> mit queue_messages.put() wird ein Element auf die Queue gepackt
# ---> mit queue_messages.get() wird ein Element aus der Queue geholt
# ---> mit queue_messages.qsize() wird die aktuelle Groesse der Queue ermittelt
# ---> mit queue_messages.empty() wird ermittelt, ob die Queue leer ist
# ---> mit queue_messages.full() wird ermittelt, ob die Queue voll ist
queue_messages=queue.Queue()
queue_measurements=queue.Queue()


# I2C-Bus
i2cbus_1=smbus.SMBus(1)

# das 16x2-LCD-Display ist mit einem I2C-Port-Expander PCF8574 verbunden
# -> das PCF8574 funktioniert wie ein Schieberegister
# -> Anschluss der Pins am PCF8574: 0b D7 D6 D5 D4 BacklightLED E RW RS
slave_lcd=0x27

slave_ds3231=0x68

# (der EEPROM hat unter Linux auf dem RPi die Adresse 0x50; in Verbindung mit einem uC hat es die Adresse 0xA1 (=Read) bzw, 0xA0 (=Write) )
slave_eeprom=0x50


# -> Pause von 2.5 sec
time.sleep(2.5)

### Ende 'Definitionen' ###
### Start 'Initialisierungen' ###

# Initialisierung des 16x2-LCD
# -> Einstellung auf 4-Bit-Modus
#    (im 4-Bit-Modus muss immer zuerst das MSB, danach das LSB folgen!)
#
# WICHTIG: dem 16x2-LCD-Display muss nach Anlegen der Versorgungsspannung eine Zeit von >15 ms fuer seine eigenen Initialisierungen gegeben werden
time.sleep(0.02)

# 1. Durchlauf
i2cbus_1.write_byte(slave_lcd, 0x3C)
time.sleep(0.00001)
i2cbus_1.write_byte(slave_lcd, 0x38)
# -> es muss mind. 4.1 ms gewartet werden
time.sleep(0.0041)

# 2. Durchlauf
i2cbus_1.write_byte(slave_lcd, 0x3C)
time.sleep(0.00001)
i2cbus_1.write_byte(slave_lcd, 0x38)
# -> es muss mind. 100 us gewartet werden
time.sleep(0.0001)

# 3. Durchlauf
i2cbus_1.write_byte(slave_lcd, 0x3C)
time.sleep(0.00001)
i2cbus_1.write_byte(slave_lcd, 0x38)
time.sleep(0.001)

# Einstellung auf 4-Bit-Modus
# (sobald der 4-Bit-Modus eingestellt ist, muss immer zuerst das MSB und danach das LSB gesendet werden!)
i2cbus_1.write_byte(slave_lcd, 0x2C)
time.sleep(0.00001)
i2cbus_1.write_byte(slave_lcd, 0x28)
time.sleep(0.001)

# -> Display on, Cursor on, Cursorblink off
# --> MSB
i2cbus_1.write_byte(slave_lcd, 0x0C)
time.sleep(0.00001)
i2cbus_1.write_byte(slave_lcd, 0x08)
time.sleep(0.001)
# --> LSB
i2cbus_1.write_byte(slave_lcd, 0xCC)
time.sleep(0.00001)
i2cbus_1.write_byte(slave_lcd, 0xC8)
time.sleep(0.001)

# -> Displayinhalt loeschen
CANBus_LCD.ClearDisplay(i2cbus_1, slave_lcd)

# Init-Text anzeigen
CANBus_LCD.InitText(i2cbus_1, slave_lcd)

# Zeichen geben, dass Initialisierungen abgeschlossen sind
for i in range(0,5):
    GPIO.output(BUILTINLED, GPIO.HIGH)
    GPIO.output(EXTERNALLED, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(BUILTINLED, GPIO.LOW)
    GPIO.output(EXTERNALLED, GPIO.LOW)
    time.sleep(0.1)

GPIO.output(BUILTINLED, GPIO.LOW)
GPIO.output(EXTERNALLED, GPIO.LOW)

### Ende 'Initialisierungen' ###
### Start 'main()' ###

# -> Echtzeituhr DS3231 einstellen
# ---> Format: dd-mm-yy hh:mm:ss
datumZeit=input('Bitte das Datum und die Uhrzeit im Format dd-mm-yy hh:mm:ss eingeben: ')
d_1=datumZeit[1:2]
d_10=datumZeit[:1]
m_1=datumZeit[4:5]
m_10=datumZeit[3:4]
y_1=datumZeit[7:8]
y_10=datumZeit[6:7]
h_1=datumZeit[10:11]
h_10=datumZeit[9:10]
min_1=datumZeit[13:14]
min_10=datumZeit[12:13]
s_1=datumZeit[16:]
s_10=datumZeit[15:16]

CANBus_DS3231.Write_Minutes(int(min_1), int(min_10), i2cbus_1, slave_ds3231)
CANBus_DS3231.Write_Hours(int(h_1), int(h_10), i2cbus_1, slave_ds3231)
CANBus_DS3231.Write_Day(int(d_1), int(d_10), i2cbus_1, slave_ds3231)
CANBus_DS3231.Write_Month(int(m_1), int(m_10), i2cbus_1, slave_ds3231)
CANBus_DS3231.Write_Year(int(y_1), int(y_10), i2cbus_1, slave_ds3231)

# -> aktuelle Zeit nur einmal vor Start der Messung aus der RTC holen
secs=CANBus_DS3231.Read_Seconds(i2cbus_1, slave_ds3231)
minutes=CANBus_DS3231.Read_Minutes(i2cbus_1, slave_ds3231)
hours=CANBus_DS3231.Read_Hours(i2cbus_1, slave_ds3231)
days=CANBus_DS3231.Read_Date(i2cbus_1, slave_ds3231)
months=CANBus_DS3231.Read_Month(i2cbus_1, slave_ds3231)
years=CANBus_DS3231.Read_Year(i2cbus_1, slave_ds3231)

datum=str(days[0])+str(days[1])+'-'+str(months[0])+str(months[1])+'-'+str(years[0])+str(years[1])
uhrzeit=str(hours[0])+str(hours[1])+'-'+str(minutes[0])+str(minutes[1])+'-'+str(secs[0])+str(secs[1])


# Log-Dateien
# a) Log-Datei fuer Messwerte festlegen
measurementsFile='/home/niklas/eigene_Programme_niklas/CANBus/Log/CANBus_logging_'+datum+'_'+uhrzeit+'.csv'
externalFile_1=open(measurementsFile, 'w')

# b) Kraftstoffverbrauch
consumptionFile='/home/niklas/eigene_Programme_niklas/CANBus/Log/CANBus_logging_consumption_'+datum+'_'+uhrzeit+'.csv'
externalFile_2=open(consumptionFile, 'w')


car=input('Bitte das auszulesende Fahrzeug eingeben (WICHTIG: Kein Leerzeichen eingeben!): ')
bit_Identifier=input('Bitte Bit-Identifier eingeben (1: 11-Bit-ID, 2: 29-Bit-ID): ')

# -> Wahl zwischen 11-Bit-ID und 28-Bit-ID
# ---> 11-Bit-ID
if(bit_Identifier=='1'):
    extendedID=False
    pidRequest=CANBus_PIDs.PID_REQUEST_11ID
# ---> 29-Bit-ID
elif(bit_Identifier=='2'):
    extendedID=True
    pidRequest=CANBus_PIDs.PID_REQUEST_29ID


# -> vor dem Start der Messung den aktuellen Tankinhalt und die bisher gefahrene Reichweite in einer Queue merken
CAN_Botschaft_withQueue(canbus_1, pidRequest, extendedID, CANBus_PIDs.FUEL_TANK_LEVEL, queue_messages)
time.sleep(0.5)
CAN_Botschaft_withQueue(canbus_1, pidRequest, extendedID, CANBus_PIDs.DISTANCE_TRAVEL_SINCE_CLEARDTCS, queue_messages)
time.sleep(2.5)

os.system('clear')
CANBus_LCD.ClearDisplay(i2cbus_1, slave_lcd)

try:
    while True:

        Ausgabe()

        # nach dem Auslesen eines Satz an Messwerte vom zentralen Gateway des CAN-Bus 2.5 sec. warten
        # -> Kuehlmitteltemperatur auslesen
        CAN_Botschaft(canbus_1, pidRequest, extendedID, CANBus_PIDs.ENGINE_COOLANT_TEMPERATURE, count, externalFile_1, count_output, queue_measurements)
        GPIO.output(BUILTINLED, GPIO.HIGH)
        GPIO.output(EXTERNALLED, GPIO.HIGH)
        count_output+=1
        time.sleep(0.25)

        # -> Drehzahl auslesen
        CAN_Botschaft(canbus_1, pidRequest, extendedID, CANBus_PIDs.ENGINE_SPEED, count, externalFile_1, count_output, queue_measurements)
        GPIO.output(BUILTINLED, GPIO.LOW)
        GPIO.output(EXTERNALLED, GPIO.LOW)
        count_output+=1
        time.sleep(0.25)

        # -> Fahrgeschwindigkeit
        CAN_Botschaft(canbus_1, pidRequest, extendedID, CANBus_PIDs.VEHICLE_SPEED, count, externalFile_1, count_output, queue_measurements)
        GPIO.output(BUILTINLED, GPIO.HIGH)
        GPIO.output(EXTERNALLED, GPIO.HIGH)
        count_output+=1
        time.sleep(0.25)

        # -> absolute Gaspedalstellung
        CAN_Botschaft(canbus_1, pidRequest, extendedID, CANBus_PIDs.THROTTLE, count, externalFile_1, count_output, queue_measurements)
        GPIO.output(BUILTINLED, GPIO.LOW)
        GPIO.output(EXTERNALLED, GPIO.LOW)
        count_output+=1
        time.sleep(0.25)

        # -> Motorlaufzeit
        CAN_Botschaft(canbus_1, pidRequest, extendedID, CANBus_PIDs.RUN_TIME_ENGINE, count, externalFile_1, count_output, queue_measurements)
        GPIO.output(BUILTINLED, GPIO.HIGH)
        GPIO.output(EXTERNALLED, GPIO.HIGH)
        count_output+=1
        time.sleep(0.25)

        # -> relative Gaspedalstellung
        CAN_Botschaft(canbus_1, pidRequest, extendedID, CANBus_PIDs.THROTTLE_RELATIVE, count, externalFile_1, count_output, queue_measurements)
        GPIO.output(BUILTINLED, GPIO.LOW)
        GPIO.output(EXTERNALLED, GPIO.LOW)
        count_output+=1
        time.sleep(0.25)

        # -> Umgebungstemperatur
        CAN_Botschaft(canbus_1, pidRequest, extendedID, CANBus_PIDs.AMBIENT_AIR_TEMPERATURE, count, externalFile_1, count_output, queue_measurements)
        GPIO.output(BUILTINLED, GPIO.HIGH)
        GPIO.output(EXTERNALLED, GPIO.HIGH)
        count_output+=1
        time.sleep(0.25)

        # -> Umgebungsdruck
        CAN_Botschaft(canbus_1, pidRequest, extendedID, CANBus_PIDs.BAROMETRIC_PRESSURE, count, externalFile_1, count_output, queue_measurements)
        GPIO.output(BUILTINLED, GPIO.LOW)
        GPIO.output(EXTERNALLED, GPIO.LOW)
        count_output+=1
        time.sleep(0.25)

        # -> Motorlast
        CAN_Botschaft(canbus_1, pidRequest, extendedID, CANBus_PIDs.ENGINE_LOAD_CALCULATED, count, externalFile_1, count_output, queue_measurements)
        GPIO.output(BUILTINLED, GPIO.HIGH)
        GPIO.output(EXTERNALLED, GPIO.HIGH)
        count_output+=1
        time.sleep(0.25)

        # -> Totpunkt
        CAN_Botschaft(canbus_1, pidRequest, extendedID, CANBus_PIDs.TIMING_ADVANCE, count, externalFile_1, count_output, queue_measurements)
        GPIO.output(BUILTINLED, GPIO.LOW)
        GPIO.output(EXTERNALLED, GPIO.LOW)
        count_output+=1
        time.sleep(0.25)

        # -> Oxygen-Sensor
        CAN_Botschaft(canbus_1, pidRequest, extendedID, CANBus_PIDs.OXYGEN_SENSOR_1, count, externalFile_1, count_output, queue_measurements)
        GPIO.output(BUILTINLED, GPIO.HIGH)
        GPIO.output(EXTERNALLED, GPIO.HIGH)
        count_output+=1
        time.sleep(0.25)

        # -> SFT
        CAN_Botschaft(canbus_1, pidRequest, extendedID, CANBus_PIDs.SHORT_TERM_FUEL_TRIM, count, externalFile_1, count_output, queue_measurements)
        GPIO.output(BUILTINLED, GPIO.LOW)
        GPIO.output(EXTERNALLED, GPIO.LOW)
        count_output+=1
        time.sleep(0.25)

        # -> LFT
        CAN_Botschaft(canbus_1, pidRequest, extendedID, CANBus_PIDs.LONG_TERM_FUEL_TRIM, count, externalFile_1, count_output, queue_measurements)
        GPIO.output(BUILTINLED, GPIO.HIGH)
        GPIO.output(EXTERNALLED, GPIO.HIGH)
        count_output+=1
        time.sleep(0.25)


        count+=1
        CANBus_LCD.WriteMeasurements(i2cbus_1, slave_lcd, queue_measurements)

        # 2.5 sec warten (!)
        #time.sleep(2.5)

        # anstatt Pause die aktuelle Zeit vom RTC auf dem LCD anzeigen und als Pause nutzen (!)
        time.sleep(2)
        CANBus_LCD.ClearDisplay(i2cbus_1, slave_lcd)
        AktuelleZeit_RTC(i2cbus_1, slave_ds3231, slave_lcd)

        os.system('clear')

except KeyboardInterrupt:
    externalFile_1.close()
    GPIO.output(BUILTINLED, GPIO.LOW)
    GPIO.output(EXTERNALLED, GPIO.LOW)
    CANBus_LCD.ClearDisplay(i2cbus_1, slave_lcd)
    CANBus_LCD.InitText(i2cbus_1, slave_lcd)

    # Empfangene und gesendete Packete auf der can0-Schnittstelle ermitteln
    #
    # -> der Parameter '-m 1' beim Befehl grep heisst, dass nach dem ersten Treffer beendet werden muss (!)
    os.system('ifconfig > interface.txt')
    for i in range(1,3):
        # zuerst die RX-Packets ermitteln
        if(i==1):
            command_interface='grep -m 1 "RX packets" interface.txt'
        # danach die TX-Packets ermitteln
        elif(i==2):
            command_interface='grep -m 1 "TX packets" interface.txt'
        
        rxtx=subprocess.check_output(command_interface, shell=True)
        rxtx_str=str(rxtx)
        rxtx_len=len(rxtx_str)

        for j in range(0,10):
            value=rxtx_len+j
            if(rxtx_len==value):
                value=23+j
                rxtx_packets=rxtx_str[21:value]
                # (Eventuelle um 2 Packete inkrementieren)
                rxtx_packets_bytes=int(rxtx_packets)*8
                rxtx_packets_kBytes=rxtx_packets_bytes/1000
                
                if(i==1):
                    print('can0-Schnittstelle')
                    print('Empfangene RX-Packete:',rxtx_packets,' => ',rxtx_packets_bytes,' B =',rxtx_packets_kBytes,' kB')
                elif(i==2):
                    print('Gesendete TX-Packete:',rxtx_packets,' => ',rxtx_packets_bytes,' B =',rxtx_packets_kBytes,' kB')
                break


    # nach der Messung bzw. Fahrt den Tankinhalt und die bisher gefahrenen Kilometer erneut in der Queue merken
    CAN_Botschaft_withQueue(canbus_1, pidRequest, extendedID, CANBus_PIDs.FUEL_TANK_LEVEL, queue_messages)
    time.sleep(0.5)
    CAN_Botschaft_withQueue(canbus_1, pidRequest, extendedID, CANBus_PIDs.DISTANCE_TRAVEL_SINCE_CLEARDTCS, queue_messages)
    time.sleep(1)

    # pruefen, ob die Queue voll ist
    if queue_messages.empty() is not None:
        # pruefen, ob 4 Elemente in der Queue sind
        if queue_messages.qsize()==4:

            ## alten Verbrauchswert aus dem EEPROM holen
            # (der Wert liegt am Speicherort 0x0001 und 0x0002)
            #old_consumption_1=CANBus_AT24C256.Read_EEPROM(0x01, i2cbus_1, slave_eeprom, 0x00)
            #time.sleep(1)
            #old_consumption_2=CANBus_AT24C256.Read_EEPROM(0x02, i2cbus_1, slave_eeprom, 0x00)
            #print('Verbrauch der vergangenen Fahrt: '+str(old_consumption_1)+'.'+str(old_consumption_2))

            fuelTank_before=queue_messages.get()
            distanceTravel_before=queue_messages.get()
            fuelTank_after=queue_messages.get()
            distanceTravel_after=queue_messages.get()
            delta_fuelTank=fuelTank_after-fuelTank_before
            delta_distanceTravel=distanceTravel_after-distanceTravel_before

            # -> nur den Verbrauch berechnen, wenn eine Reichweite >0 erreicht wurde
            if delta_distanceTravel>0:
                consumption=(delta_fuelTank*100)/delta_distanceTravel
                
                # -> Betrag bilden, wenn der Wert <0 ist
                if(consumption<0):
                    consumption=consumption*(-1)

                # neuen Verbrauchswert im EEPROM speichern
                # (neuen Wert an denselben Speicherort des EEPROM schreiben, an dem der alte Werte ist, also auf 0x0001 und 0x0002)
                #consumption_parts=Convert_FloatNumber(consumption)
                #CANBus_AT24C256.Write_EEPROM(0x01, consumption_parts[0], i2cbus_1, slave_eeprom, 0x00)
                #time.sleep(1)
                #CANBus_AT24C256.Write_EEPROM(0x02, consumption_parts[1], i2cbus_1, slave_eeprom, 0x00)
            else:
                consumption=0
            
            externalFile_2.write('Verbrauch am '+datum+' ('+uhrzeit+'): '+str(consumption)+' l/100km'+'\n')
            print('Heutiger Verbrauch: '+str(consumption)+' l/100km')
        else:
            print('Die Queue ist voll, aber mit fehlenden CAN-Bus-Botschaften.')
    else:
        print('Die Queue ist leer.')
    externalFile_2.close()


    print('Auswertung beginnt...')
    for i in range(0,5):
        GPIO.output(EXTERNALLED, GPIO.HIGH)
        time.sleep(0.05)
        GPIO.output(EXTERNALLED, GPIO.LOW)
        time.sleep(0.05)

    # -> in einen neuen Ordner werden alle Diagramme abgelegt
    #name_measurementsWithDiagrams='Messwerte vom '
    folder_measurementsWithDiagrams='Messwerte_'+car+'_'+datum+'_'+uhrzeit
    directory_measurementsWithDiagrams=directory+folder_measurementsWithDiagrams
    os.system('mkdir '+directory_measurementsWithDiagrams)

    # Auswertung bzw. Messwerte in Diagramme plotten
    rows=(count-1)*13
    matrix_values=numpy.zeros([rows,4])
    print('Zur Kontrolle: Anzahl eingetragener Messwerte: '+str(count))

    # -> Messwerte in eine Matrix umpacken
    with open(measurementsFile) as csvfile:
        read_csvFile=csv.reader(csvfile, delimiter=';')

        i=0
        j=0

        # -> zuerst die Zeilen, dann die Spalten durchgehen
        for row in read_csvFile:

            # -> den Inhalt der csv-Datei in eine Matrix fuellen
            if j==rows+1:
                pass
            elif j>=0:
                for i in range(0,3):
                    if i==1:
                        pass
                    else:
                        matrix_values[j-1,i]=row[i]
            j=j+1

    # -> Werte zum Zeichnen in eigene Arrays packen
    a1=0
    a2=1
    a3=2
    a4=3
    a5=4
    a6=5
    a7=6
    a8=7
    a9=8
    a10=9
    a11=10
    a12=11
    a13=12

    real_rows=int((rows/13)-1)

    for i in range(0,real_rows):
        # -> x- und y-Werte zum Zeichnen befuellen
        nr_x.append(j)
        drehzahl_y.append(matrix_values[a1,2])
        fahrgeschwindigkeit_y.append(matrix_values[a2,2])
        throttle_absolute_y.append(matrix_values[a3,2])
        motorlaufzeit_y.append(matrix_values[a4,2])
        throttle_relative_y.append(matrix_values[a5,2])
        umgebungstemperatur_y.append(matrix_values[a6,2])
        umgebungsdruck_y.append(matrix_values[a7,2])
        motorlast_y.append(matrix_values[a8,2])
        totpunkt_y.append(matrix_values[a9,2])
        oxygen_y.append(matrix_values[a10,2])
        sft_y.append(matrix_values[a11,2])
        lft_y.append(matrix_values[a12,2])
        kuehlmitteltemperatur_y.append(matrix_values[a13,2])

        a1+=13
        a2+=13
        a3+=13
        a4+=13
        a5+=13
        a6+=13
        a7+=13
        a8+=13
        a9+=13
        a10+=13
        a11+=13
        a12+=13
        a13+=13
        j=j+1

    # -> Zeichnen
    for i in range(0,13):
        # -> nur Kuehlmitteltemperatur
        if i==0:
            y=kuehlmitteltemperatur_y
            y_axis='ECT [*C]'
            name='Kuehlmitteltemperatur'
        # -> nur Drehzahl
        elif i==1:
            y=drehzahl_y
            y_axis='n [rpm]'
            name='Drehzahl'
        # -> nur Fahrgeschwindigkeit
        elif i==2:
            y=fahrgeschwindigkeit_y
            y_axis='v [km/h]'
            name='Fahrgeschwindigkeit'
        # -> nur absolute Gaspedalstellung
        elif i==3:
            y=throttle_absolute_y
            y_axis='APP [%]'
            name='Absolute Gaspedalstellung'
        # -> nur Motorlaufzeit
        elif i==4:
            y=motorlaufzeit_y
            y_axis='RUNTM [sec.]'
            name='Motorlaufzeit'
        # -> nur relative Gaspedalstellung
        elif i==5:
            y=throttle_relative_y
            y_axis='TP_R [%]'
            name='Relative Gaspedalstellung'
        # -> nur Umgebungstemperatur
        elif i==6:
            y=umgebungstemperatur_y
            y_axis='AAT [*C]'
            name='Umgebungstemperatur'
        # -> nur Umgebungsdruck
        elif i==7:
            y=umgebungsdruck_y
            y_axis='p [bar]'
            name='Umgebungsdruck'
        # -> nur Motorlast
        elif i==8:
            y=motorlast_y
            y_axis='R [%]'
            name='Motorlast'
        # -> nur Totpunkt
        elif i==9:
            y=totpunkt_y
            y_axis='BTC [*]'
            name='Totpunkt'
        # -> nur Oxygen-Sensor
        elif i==10:
            y=oxygen_y
            y_axis='O2 [1]'
            name='O2'
        # -> nur SFT
        elif i==11:
            y=sft_y
            y_axis='SFT [%]'
            name='SFT'
        # -> nur LFT
        elif i==12:
            y=lft_y
            y_axis='LFT [%]'
            name='LFT'

        file_measurement=directory_measurementsWithDiagrams+'/'+'Messwerte von '+name+' am '+datum+' - '+uhrzeit+'.png'
        figure=plt.figure(figsize=(8,7))
        plt.title(name+' des '+car+' am '+datum+' - '+uhrzeit)
        plt.xlabel('Messungen')
        plt.ylabel(y_axis)
        plt.plot(nr_x, y, '-', color='red')
        plt.savefig(file_measurement)

    # ein Diagramm mit allen wichtigen Parametern zeichnen
    file_measurements=directory_measurementsWithDiagrams+'/'+'Fahrparameter vom '+datum+' - '+uhrzeit+'.png'
    figure=plt.figure(figsize=(8,7))
    plt.title('Fahrt mit '+car+' am '+datum+' - '+uhrzeit)
    plt.xlabel('Messungen')
    plt.ylabel('ECT [*C], v [km/h], APP [%], AAT [*C], TP_R [%], r [%], BTC [*]')
    plt.plot(nr_x, kuehlmitteltemperatur_y, '-', color='red', label='Engine Coolant Temperature')
    plt.plot(nr_x, fahrgeschwindigkeit_y, '-', color='blue', label='Vehicle Speed')
    plt.plot(nr_x, throttle_absolute_y, '-', color='green', label='Absolute Throttle')
    plt.plot(nr_x, totpunkt_y, '-', color='yellow', label='Timing Advance')
    plt.plot(nr_x, motorlast_y, '-', color='black', label='Engine Load Calculated')
    plt.plot(nr_x, umgebungstemperatur_y, '-', color='cyan', label='Ambient Air Temperature')
    plt.plot(nr_x, throttle_relative_y, '-', color='pink', label='Relative Throttle')
    plt.legend()
    plt.savefig(file_measurements)

    # alle Diagramme im dafuer extra angelegten Ordner zu einem Archiv verpacken
    # (wichtig: beim Erstellen eines Archivs muessen die zu verpackenden Elemente in demselben Verzeichnis sein, in dem auch das zu erstellende Archiv ist)
    #os.system(' tar -cf '+folder_measurementsWithDiagrams+'.tar '+folder_measurementsWithDiagrams)

    for i in range(0,5):
        GPIO.output(EXTERNALLED, GPIO.HIGH)
        time.sleep(0.05)
        GPIO.output(EXTERNALLED, GPIO.LOW)
        time.sleep(0.05)
    
    print('Auswertung abgeschlossen, Programm beendet.')
    GPIO.output(EXTERNALLED, GPIO.LOW)
    CANBus_LCD.ClearDisplay(i2cbus_1, slave_lcd)

### Ende 'main()' ###


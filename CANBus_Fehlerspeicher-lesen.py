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
import CANBus_PIDs
import CANBus_SIDs
import csv


def Datum():
    aktuelles_Datum=datetime.date.today()
    aktuelles_Datum=str(aktuelles_Datum.day)+'-'+str(aktuelles_Datum.month)+'-'+str(aktuelles_Datum.year)

    return aktuelles_Datum


def Uhrzeit():
    zeit=time.asctime();
    zeit=str(zeit)
    zeit=zeit[11:19]
    zeit=zeit[:2]+'-'+zeit[3:5]+'-'+zeit[6:]

    return zeit


def CANBus_transmit(bus_1, request, pci, sid, pid):
    # -> als CAN-Bus-Botschaft wird ein (Standard) Data-Frame zum Abfragen von Messwerten gesendet
    # -> der DLC (= Data Length Code) ist 8, also 8 Byte Nutzdaten
    # -> in der Liste data sind die 8 Byte Nutzdaten
    # -> arbitration_id ist der Indentifier des Arbitration Field (das Arbitration Field besteht aus dem Identifier und dem RTR)
    message=can.Message(arbitration_id=request, data=[pci,sid,pid,0x00,0x00,0x00,0x00,0x00], extended_id=False)
    bus_1.send(message)
    time.sleep(0.05)


def CANBus_receive(bus_1, timeout):
    msg=bus_1.recv(timeout)

    return msg


def CAN_Botschaft(bus_1, request, pci_xxx, sid_xxx, pid_xxx, queue_1, i, file):
    # -> Anfrage fuer eine bestimmte CAN-Bus-Botschaft stellen
    CANBus_transmit(bus_1, request, pci_xxx, sid_xxx, pid_xxx)
    print('CAN-Bus-Botschaft ist gesendet.')

    # -> Antwirt zur gestellten Anfrage bekommen
    message=CANBus_receive(bus_1, 100)

    if message is None:
        print('Timeout erreicht, keine CAN-Bus-Botschaft.')
    else:
        queue_1.put(message)

        file.write(str(i)+' Empfangene CAN-Bus-Nachricht: '+str(message)+'\n')
        
        # VIN (=Vehicle Identification Number bzw. Fahrzeug-Identifizierungsnummer)
        if(sid_xxx==0x09):
            print('1. Teil der VIN: '+str(message))

            # -> um die vollstaendie VIN (= Vehicle Identification Number) zu bekommen, muss eine CAN-ID 0x7E8-8=0x7E0 (= es ist eine flow-control-message, die aus der CAN-ID Antwort des ECU minus 8 besteht) als Anfrage gesendet werden, um die restlichen Bytes der VIN zu bekommen
            #    (die Daten bei der Anfrage, um die restlichen Bytes der VIN zu bekommen, sind: 0x30 0x00 0x00 0x00 0x00 0x00 0x00 0x00)
            # -> HINWEIS: die VIN besteht aus 17 Bytes und ist in 3 Teile aufgeteilt: a) die ersten 3 Bytes sind World Manufacturer Identifier (= WMI)
            #                                                                         b) die naechsten 6 Bytes sind Vehicle Description Section (= VDS)
            #                                                                         c) die letzten 8 Byte sind Vehicle Identifier Section (= VIS)
            #             (siehe die Norm ISO 3779 zur VIN)
            CANBus_transmit(bus_1, 0x7E0, 0x30, 0x00, 0x00)
            message=CANBus_receive(bus_1, 100)
            print('2. Teil der VIN: '+str(message))
            message=CANBus_receive(bus_1, 100)
            print('3. Teil der VIN: '+str(message))
        # DTCs-Fehler
        elif(sid_xxx==0x03):
            if(message.data[2]==0x00):
                print('Es liegen keine Fehler vor.')
            else:
                print('Es gibt Fehler.')
        # vorlaeufige-DTCs-Fehler
        elif(sid_xxx==0x07):
            if(message.data[2]==0x00):
                print('Es liegen auch keine vorlaeufigen Fehler vor.')
            else:
                print('Es gibt vorlaeufige Fehler.')

        print('CAN-Bus-Botschaft empfangen.')



### Start 'Definitionen' ###
BUILTINLED=22

count=1
command_interface='cat /sys/class/net/can0/operstate'

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

# pruefen, ob die CAN-Bus-Schnittxtelle can0 an ist
# (die Funktion os.system() liefert keinen Rueckgabewert im Vergleich zu subprocess.check_output)
can0_state=subprocess.check_output(command_interface, shell=True)

if(can0_state==b'down\n'):
    # (die meisten CAN-Bus-Netze im Auto haben eine Baudrate von 500000
    os.system('/sbin/ip link set can0 up type can bitrate 500000')
    print('can0 eingeschalten.')
else:
    print('can0 ist schon an.')


# CAN-Bus-Schnittstelle can0 festlegen
canbus_1=can.interface.Bus(channel='can0', bustype='socketcan_native')
#canbus_1=can.interface.Bus(channel='can0', bustype='socketcan_ctypes')

# Queue definieren
# (es wird die Bibliothek 'queue' gebraucht)
# -> die Queue arbeitet nach dem Prinzip FIFO (es ist ein Stapelspeicher)
#    (mit der Bibliothek asyncio.LifoQueue kann auch eine Queue nach dem Prinzip LIFO erstellt werden: queue_messages=asyncio.LifoQueue() )
# ---> mit queue_messages.Queue(maxsize=5) kann die max. Groesse der Queue auf 5 Elemente begrenzt werden
# ---> mit queue_messages.put() wird ein Element auf die Queue gepackt
# ---> mit queue_messagesprint('Programm beendet.').get() wird ein Element aus der Queue geholt
# ---> mit queue_messages.qsize() wird die aktuelle Groesse der Queue ermittelt
# ---> mit queue_messages.empty() wird ermittelt, ob die Queue leer ist
# ---> mit queue_messages.full() wird ermittelt, ob die Queue voll ist
queue_messages=queue.Queue()

# Log-Datei festlegen
errorFile='/home/niklas/eigene_Programme_niklas/CANBus/Log/CANBus_ErrorLog_'+Datum()+'_'+Uhrzeit()+'.csv'
externalFile=open(errorFile, 'w')

### Ende 'Definitionen' ###
### Start 'Initialisierungen' ###

# Zeichen geben, dass Initialisierungen abgeschlossen sind
for i in range(0,5):
    GPIO.output(BUILTINLED, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(BUILTINLED, GPIO.LOW)
    time.sleep(0.5)

GPIO.output(BUILTINLED, GPIO.LOW)

### Ende 'Initialisierungen' ###
### Start 'main()' ###

# Abfragen der Fahrzeuginformationen
CAN_Botschaft(canbus_1, CANBus_PIDs.PID_REQUEST_11ID, 0x02, CANBus_SIDs.SID9, 0x02, queue_messages, count, externalFile)
count+=1
time.sleep(5)

# Abfragen, ob die MIL-Lampe leuchtet
CAN_Botschaft(canbus_1, CANBus_PIDs.PID_REQUEST_11ID, 0x02, CANBus_SIDs.SID1, CANBus_PIDs.MIL, queue_messages, count, externalFile)
count+=1
time.sleep(5)

# Abfrage der endgueltigen Fehlercodes DTCs
# (wenn kein Fehler vorliegt, dann folgt eine Antwort mit 0x0000)
CAN_Botschaft(canbus_1, CANBus_PIDs.PID_REQUEST_11ID, 0x01, CANBus_SIDs.DTCS, 0x00, queue_messages, count, externalFile)
count+=1
time.sleep(5)

# Abfrage der vorlaeufigen defekten Fehlercodes DTCs
CAN_Botschaft(canbus_1, CANBus_PIDs.PID_REQUEST_11ID, 0x01, CANBus_SIDs.PROVISIONALLY_DTCS, 0x00, queue_messages, count, externalFile)
count+=1

# Lesen der gespeicherten Fehler
# -> mit SID=0x02 kann ermittelt werden, wo genau der Fehler aufgetreten ist (also gespeicherte Umweltbedingungen); dazu muss die PID mituebergeben werden
#CAN_Botschaft(canbus_1, CANBus_PIDs.PID_REQUEST, 0x02, CANBus_SIDs.FREEZE_FRAMES, CANBus_PIDs., queue_messages, externalFile)

# Loeschen des Fehlerspeichers
#CAN_Botschaft(canbus_1, CANBus_PIDs.PID_REQUEST, 0x01, CANBus_SIDs.CLEAR_ERRORS, 0x00, queue_messages, externalFile)

# 5 sec warten (!)
time.sleep(5)


externalFile.close()
GPIO.output(BUILTINLED, GPIO.LOW)
print('Programm beendet.')

### Ende 'main()' ###


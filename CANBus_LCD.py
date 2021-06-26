#!/usr/bin/python3

import smbus
import time
import queue


def Init_LCD(i2cbus, slave):
    # Initialisierung des 16x2-LCD
    # -> Einstellung auf 4-Bit-Modus
    #    (im 4-Bit-Modus muss immer zuerst das MSB, danach das LSB folgen!)
    #
    # WICHTIG: dem 16x2-LCD-Display muss nach Anlegen der Versorgungsspannung eine Zeit von >15 ms fuer seine eigenen Initialisierungen gegeben werden
    time.sleep(0.02)

    # 1. Durchlauf
    i2cbus.write_byte(slave, 0x3C)
    time.sleep(0.00001)
    i2cbus.write_byte(slave, 0x38)
    # -> es muss mind. 4.1 ms gewartet werden
    time.sleep(0.0041)

    # 2. Durchlauf
    i2cbus.write_byte(slave, 0x3C)
    time.sleep(0.00001)
    i2cbus.write_byte(slave, 0x38)
    # -> es muss mind. 100 us gewartet werden
    time.sleep(0.0001)

    # 3. Durchlauf
    i2cbus.write_byte(slave, 0x3C)
    time.sleep(0.00001)
    i2cbus.write_byte(slave, 0x38)
    time.sleep(0.001)

    # Einstellung auf 4-Bit-Modus
    # (sobald der 4-Bit-Modus eingestellt ist, muss immer zuerst das MSB und danach das LSB gesendet werden!)
    i2cbus.write_byte(slave, 0x2C)
    time.sleep(0.00001)
    i2cbus.write_byte(slave, 0x28)
    time.sleep(0.001)

    # -> Display on, Cursor on, Cursorblink off
    # --> MSB
    i2cbus.write_byte(slave, 0x0C)
    time.sleep(0.00001)
    i2cbus.write_byte(slave, 0x08)
    time.sleep(0.001)
    # --> LSB
    i2cbus.write_byte(slave, 0xCC)
    time.sleep(0.00001)
    i2cbus.write_byte(slave, 0xC8)
    time.sleep(0.001)


def ClearDisplay(i2cbus, slave):
    # -> es muss der 4-Bit-Modus am 16x2-LCD-Display eingestellt sein!
    #
    # MSB
    i2cbus.write_byte(slave, 0x0C)
    time.sleep(0.00001)
    i2cbus.write_byte(slave, 0x08)
    time.sleep(0.001)

    # LSB
    i2cbus.write_byte(slave, 0x1C)
    time.sleep(0.00001)
    i2cbus.write_byte(slave, 0x18)
    time.sleep(0.001)


def SignWrite(i2cbus, slave, typ, nr):

    # Buchstaben
    # -> letters_msb=[a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z] => [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52]
    letters_msb=[[0x6D,0x69],[0x6D,0x69],[0x6D,0x69],[0x6D,0x69],[0x6D,0x69],[0x6D,0x69],[0x6D,0x69],[0x6D,0x69],[0x6D,0x69],[0x6D,0x69],[0x6D,0x69],[0x6D,0x69],[0x6D,0x69],[0x6D,0x69],[0x6D,0x69],[0x7D,0x79],[0x7D,0x79],[0x7D,0x79],[0x7D,0x79],[0x7D,0x79],[0x7D,0x79],[0x7D,0x79],[0x7D,0x79],[0x7D,0x79],[0x7D,0x79],[0x7D,0x79],[0x4D,0x49],[0x4D,0x49],[0x4D,0x49],[0x4D,0x49],[0x4D,0x49],[0x4D,0x49],[0x4D,0x49],[0x4D,0x49],[0x4D,0x49],[0x4D,0x49],[0x4D,0x49],[0x4D,0x49],[0x4D,0x49],[0x4D,0x49],[0x4D,0x49],[0x5D,0x59],[0x5D,0x59],[0x5D,0x59],[0x5D,0x59],[0x5D,0x59],[0x5D,0x59],[0x5D,0x59],[0x5D,0x59],[0x5D,0x59],[0x5D,0x59],[0x5D,0x59]]
    # -> letters_lsb=[a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z] => [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52]
    letters_lsb=[[0x1D,0x19],[0x2D,0x29],[0x3D,0x39],[0x4D,0x49],[0x5D,0x59],[0x6D,0x69],[0x7D,0x79],[0x8D,0x89],[0x9D,0x99],[0xAD,0xA9],[0xBD,0xB9],[0xCD,0xC9],[0xDD,0xD9],[0xED,0xE9],[0xFD,0xF9],[0x0D,0x09],[0x1D,0x19],[0x2D,0x29],[0x3D,0x39],[0x4D,0x49],[0x5D,0x59],[0x6D,0x69],[0x7D,0x79],[0x8D,0x89],[0x9D,0x99],[0xAD,0xA9],[0x1D,0x19],[0x2D,0x29],[0x3D,0x39],[0x4D,0x49],[0x5D,0x59],[0x6D,0x69],[0x7D,0x79],[0x8D,0x89],[0x9D,0x99],[0xAD,0xA9],[0xBD,0xB9],[0xCD,0xC9],[0xDD,0xD9],[0xED,0xE9],[0xFD,0xF9],[0x0D,0x09],[0x1D,0x19],[0x2D,0x29],[0x3D,0x39],[0x4D,0x49],[0x5D,0x59],[0x6D,0x69],[0x7D,0x79],[0x8D,0x89],[0x9D,0x99],[0xAD,0xA9]]

    # Zahlen
    # -> numbers_msb=[1,2,3,4,5,6,7,8,9,0] => [1,2,3,4,5,6,7,8,9,10]
    numbers_msb=[[0x3D,0x39],[0x3D,0x39],[0x3D,0x39],[0x3D,0x39],[0x3D,0x39],[0x3D,0x39],[0x3D,0x39],[0x3D,0x39],[0x3D,0x39],[0x3D,0x39]]
    # -> numbers_lsb=[1,2,3,4,5,6,7,8,9,0] => [1,2,3,4,5,6,7,8,9,10]
    numbers_lsb=[[0x1D,0x19],[0x2D,0x29],[0x3D,0x39],[0x4D,0x49],[0x5D,0x59],[0x6D,0x69],[0x7D,0x79],[0x8D,0x89],[0x9D,0x99],[0x0D,0x09]]

    # Sonderzeichen
    # -> specialSigns_msb=[=,.,:,' ',(,),-,%,*,,,!,+,*,#] => [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
    specialSigns_msb=[[0x3D,0x39],[0x2D,0x29],[0x3D,0x39],[0xFD,0xF9],[0x2D,0x29],[0x2D,0x29],[0x2D,0x29],[0x2D,0x29],[0xDD,0xD9],[0x2D,0x29],[0x2D,0x29],[0x2D,0x29],[0x2D,0x29],[0x2D,0x29]]
    # -> specialSigns_lsb=[=,.,:,' ',(,),-,%,*,,,!,+,*,#] => [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
    specialSigns_lsb=[[0xDD,0xD9],[0xED,0xE9],[0xAD,0xA9],[0xED,0xE9],[0x8D,0x89],[0x9D,0x99],[0xDD,0xD9],[0x5D,0x59],[0xFD,0xF9],[0xCD,0xC9],[0x1D,0x19],[0xBD,0xB9],[0xAD,0xA9],[0x3D,0x39]]

    # Buchstabe schreiben
    if(typ==0):
        # MSB
        i2cbus.write_byte(slave, letters_msb[nr-1][0])
        time.sleep(0.00001)
        i2cbus.write_byte(slave, letters_msb[nr-1][1])
        time.sleep(0.001)
        # LSB
        i2cbus.write_byte(slave, letters_lsb[nr-1][0])
        time.sleep(0.00001)
        i2cbus.write_byte(slave, letters_lsb[nr-1][1])
        time.sleep(0.001)
    # Zahl schreiben
    elif(typ==1):
        # MSB
        i2cbus.write_byte(slave, numbers_msb[nr-1][0])
        time.sleep(0.00001)
        i2cbus.write_byte(slave, numbers_msb[nr-1][1])
        time.sleep(0.001)
        # LSB
        i2cbus.write_byte(slave, numbers_lsb[nr-1][0])
        time.sleep(0.00001)
        i2cbus.write_byte(slave, numbers_lsb[nr-1][1])
        time.sleep(0.001)
    # Sonderzeichen schreiben
    elif(typ==2):
        # MSB
        i2cbus.write_byte(slave, specialSigns_msb[nr-1][0])
        time.sleep(0.00001)
        i2cbus.write_byte(slave, specialSigns_msb[nr-1][1])
        time.sleep(0.001)
        # LSB
        i2cbus.write_byte(slave, specialSigns_lsb[nr-1][0])
        time.sleep(0.00001)
        i2cbus.write_byte(slave, specialSigns_lsb[nr-1][1])
        time.sleep(0.001)


def LCD_SetPosition(y, x, i2cbus, slave):
    position=0x80
    zeile_1=0x00
    zeile_2=0x40

    # 1. Zeile
    if(y==1):
        data=(position|zeile_1+x)
    # 2. Zeile
    elif(y==2):
        data=(position|zeile_2+x)

    # Aufteilung der Variable 'data' in MSB und LSB
    # -> MSB
    data_msb=data&0xF0
    data_msb_1=data_msb+0x0C
    data_msb_2=data_msb+0x08

    # -> LSB
    data_lsb=data<<4
    data_lsb=data_lsb&0xF0
    data_lsb_1=data_lsb+0x0C
    data_lsb_2=data_lsb+0x08

    # nach der Uebertragung eines vollstaendigen Befehls an das 16x2-LCD muss mind. 42 us gewartet werden
    # -> MSB-Byte
    i2cbus.write_byte(slave, data_msb_1)
    time.sleep(0.00001)
    i2cbus.write_byte(slave, data_msb_2)
    time.sleep(0.001)

    # -> LSB-Byte
    i2cbus.write_byte(slave, data_lsb_1)
    time.sleep(0.00001)
    i2cbus.write_byte(slave, data_lsb_2)
    time.sleep(0.001)


def InitText(i2cbus, slave):
    LCD_SetPosition(1, 0, i2cbus, slave)
    SignWrite(i2cbus, slave, 0, 29)
    SignWrite(i2cbus, slave, 0, 27)
    SignWrite(i2cbus, slave, 0, 40)
    SignWrite(i2cbus, slave, 2, 4)
    SignWrite(i2cbus, slave, 0, 30)
    SignWrite(i2cbus, slave, 0, 9)
    SignWrite(i2cbus, slave, 0, 1)
    SignWrite(i2cbus, slave, 0, 7)
    SignWrite(i2cbus, slave, 0, 14)
    SignWrite(i2cbus, slave, 0, 15)
    SignWrite(i2cbus, slave, 0, 19)
    SignWrite(i2cbus, slave, 0, 5)
    SignWrite(i2cbus, slave, 2, 4)
    SignWrite(i2cbus, slave, 0, 2)
    SignWrite(i2cbus, slave, 0, 25)
    LCD_SetPosition(2, 0, i2cbus, slave)
    SignWrite(i2cbus, slave, 0, 14)
    SignWrite(i2cbus, slave, 0, 9)
    SignWrite(i2cbus, slave, 0, 11)
    SignWrite(i2cbus, slave, 0, 12)
    SignWrite(i2cbus, slave, 0, 1)
    SignWrite(i2cbus, slave, 0, 19)
    SignWrite(i2cbus, slave, 2, 4)
    SignWrite(i2cbus, slave, 2, 5)
    SignWrite(i2cbus, slave, 0, 44)
    SignWrite(i2cbus, slave, 0, 5)
    SignWrite(i2cbus, slave, 0, 22)
    SignWrite(i2cbus, slave, 2, 4)
    SignWrite(i2cbus, slave, 1, 1)
    SignWrite(i2cbus, slave, 2, 2)
    SignWrite(i2cbus, slave, 1, 2)
    SignWrite(i2cbus, slave, 2, 6)


def WriteNumber(number, i2cbus, slave):
    number_str=str(number)
    laenge_number=len(number_str)

    for i in range(0,laenge_number):
        if(number_str[i]=='0'):
            nr=10
        elif(number_str[i]=='1'):
            nr=1
        elif(number_str[i]=='2'):
            nr=2
        elif(number_str[i]=='3'):
            nr=3
        elif(number_str[i]=='4'):
            nr=4
        elif(number_str[i]=='5'):
            nr=5
        elif(number_str[i]=='6'):
            nr=6
        elif(number_str[i]=='7'):
            nr=7
        elif(number_str[i]=='8'):
            nr=8
        elif(number_str[i]=='9'):
            nr=9
        else:
            nr=8

        SignWrite(i2cbus, slave, 1, nr)


def WriteMeasurements(i2cbus, slave, customQueue):
    ClearDisplay(i2cbus, slave)

    # 1. Zeile
    LCD_SetPosition(1, 0, i2cbus, slave)
    SignWrite(i2cbus, slave, 0, 20)
    SignWrite(i2cbus, slave, 2, 1)
    value=customQueue.get()
    # -> pruefen, ob die Kuehlmitteltemperatur nur ein Zeichen hat
    if(len(str(value))==1):
        SignWrite(i2cbus, slave, 2, 4)
    WriteNumber(value, i2cbus, slave)
    SignWrite(i2cbus, slave, 2, 9)
    SignWrite(i2cbus, slave, 0, 29)
    SignWrite(i2cbus, slave, 2, 4)
    SignWrite(i2cbus, slave, 0, 14)
    SignWrite(i2cbus, slave, 2, 1)
    value=customQueue.get()
    # -> pruefen, ob die Drehzahl 1 Zeichen oder nur 3 Zeichen hat
    if(len(str(value))==1):
        for i in range(0,3):
            SignWrite(i2cbus, slave, 2, 4)
    elif(len(str(value))==3):
        SignWrite(i2cbus, slave, 2, 4)
    WriteNumber(value, i2cbus, slave)
    SignWrite(i2cbus, slave, 0, 18)
    SignWrite(i2cbus, slave, 0, 16)
    SignWrite(i2cbus, slave, 0, 13)

    # 2. Zeile
    LCD_SetPosition(2, 0, i2cbus, slave)
    SignWrite(i2cbus, slave, 0, 46)
    SignWrite(i2cbus, slave, 0, 42)
    SignWrite(i2cbus, slave, 2, 1)
    value=customQueue.get()
    # -> pruefen, ob relative Gaspedalstellung nur 1 Zeichen hat
    if(len(str(value))==1):
        SignWrite(i2cbus, slave, 2, 4)
    WriteNumber(value, i2cbus, slave)
    # -> Nachkommastelle hinzufuegen
    SignWrite(i2cbus, slave, 2, 2)
    value=customQueue.get()
    WriteNumber(value, i2cbus, slave)
    SignWrite(i2cbus, slave, 2, 8)
    SignWrite(i2cbus, slave, 2, 4)
    SignWrite(i2cbus, slave, 0, 44)
    SignWrite(i2cbus, slave, 2, 1)
    value=customQueue.get()
    # -> pruefen, ob die Motorlast nur ein Zeichen hat
    if(len(str(value))==1):
        SignWrite(i2cbus, slave, 2, 4)
    WriteNumber(value, i2cbus, slave)
    # -> Nachkommastelle hinzufuegen
    SignWrite(i2cbus, slave, 2, 2)
    value=customQueue.get()
    WriteNumber(value, i2cbus, slave)
    SignWrite(i2cbus, slave, 2, 8)


def Write_Time(i2cbus, slave, datum, uhrzeit):
    ClearDisplay(i2cbus, slave)

    for i in range(0,2):
        if(i==0):
            len_string=len(datum)
            text=datum

            LCD_SetPosition(1, 1, i2cbus, slave)
            SignWrite(i2cbus, slave, 2, 13)
            SignWrite(i2cbus, slave, 2, 13)
            LCD_SetPosition(1, 4, i2cbus, slave)
        elif(i==1):
            #LCD_SetPosition(2, 4, i2cbus, slave)
            len_string=len(uhrzeit)
            text=uhrzeit

            LCD_SetPosition(2, 1, i2cbus, slave)
            SignWrite(i2cbus, slave, 2, 14)
            SignWrite(i2cbus, slave, 2, 14)
            LCD_SetPosition(2, 4, i2cbus, slave)

        for j in range(0,len_string):
            if(text[j]=='1'):
                SignWrite(i2cbus, slave, 1, 1)
            elif(text[j]=='2'):
                SignWrite(i2cbus, slave, 1, 2)
            elif(text[j]=='3'):
                SignWrite(i2cbus, slave, 1, 3)
            elif(text[j]=='4'):
                SignWrite(i2cbus, slave, 1, 4)
            elif(text[j]=='5'):
                SignWrite(i2cbus, slave, 1, 5)
            elif(text[j]=='6'):
                SignWrite(i2cbus, slave, 1, 6)
            elif(text[j]=='7'):
                SignWrite(i2cbus, slave, 1, 7)
            elif(text[j]=='8'):
                SignWrite(i2cbus, slave, 1, 8)
            elif(text[j]=='9'):
                SignWrite(i2cbus, slave, 1, 9)
            elif(text[j]=='0'):
                SignWrite(i2cbus, slave, 1, 10)
            elif(text[j]=='-'):
                SignWrite(i2cbus, slave, 2, 7)
            elif(text[j]==':'):
                SignWrite(i2cbus, slave, 2, 3)

        if(i==0):
            LCD_SetPosition(1, 13, i2cbus, slave)
            SignWrite(i2cbus, slave, 2, 13)
            SignWrite(i2cbus, slave, 2, 13)
        elif(i==1):
            LCD_SetPosition(2, 13, i2cbus, slave)
            SignWrite(i2cbus, slave, 2, 14)
            SignWrite(i2cbus, slave, 2, 14)



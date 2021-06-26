#!/usr/bin/pyhon3

# Anfrage an ECUs
PID_REQUEST_11ID=0x7DF
PID_REQUEST_29ID=0x18DB33F1

# Kuehlwassertemperatur
# -> Hinweis: Es wird mit ECT = Engine Coolant Temperature angekuerzt
# -> Einheit: *C
ENGINE_COOLANT_TEMPERATURE=0x05
#ENGINE_COOLANT_TEMPERATURE=0x67

# Drehzahl
# -> Hinweis: Es wird mit RPM = Revolutions per minute angekuerzt
# -> Einheit: rpm => (256*vlue+value)/4
ENGINE_SPEED=0x0C

# Fahrgeschwindigkeit
# -> Einheit: km/h
VEHICLE_SPEED=0x0D

# -> Einheit: *C
INTAKE_AIR_TEMPERATURE=0x0F

# Luftdurchfluss
# -> Hinweis: Es ist der Luftmassenmesser
# ->Einheit: g/s => (256*value+value)/4
MASS_AIR_FLOW_SENSOR_a=0x10
# oder
MASS_AIR_FLOW_SENSOR_b=0x66

# Gaspedal bzw. absolute Drosselklappenstellung
# -> Hinweis: Es wird mit APP = Accelerator Pedal Position abgekuerzt
# -> Einheit: % => (100/255)*value
THROTTLE=0x11

# Zeit seit Motorstart
# -> Hinweis: Es wird mit RUNTM abgekuerzt
# -> Einheit: sec. => 256*value+value
RUN_TIME_ENGINE=0x1F

# Relative Gaspedalstellung
# -> Hinweis: Es wird mit TP_R Throttle Position oder TP_R = Throttle Position Relative abgekuerzt
# -> Einheit: % => (100/255)*value
THROTTLE_RELATIVE=0x45

# Umgebungstemperatur
# -> Hinweis: Es wird mit AAT = Ambient Air Temperature abgekuerzt
# -> Einheit: *C => value-40
AMBIENT_AIR_TEMPERATURE=0x46

# -> Einheit: *C
#ENGINE_OIL_TEMPERATURE=0x5C

# MIL-Lampe und Anzahl der Fehler im Fehlerspeicher
MIL=0x01

# Status des Einspritzsystems
FUEL_SYSTEM_STATUS=0x03

# berechneter Lastabwurf
# -> Einheit: % => (100/255)*value
ENGINE_LOAD_CALCULATED=0x04

# Kraftstoffdruck
# -> Einheit: 3*value
FUEL_PRESSURE=0x0A

# Fahrsterecke seit MIL-Lampe gesetzt ist
# -> Einheit: km
DISTANCE_TRAVEL_WITH_MIL=0x21

# Kraftstoffdruck
# -> Einheit: kPa => 10*(256*value+value)
FUEL_RAIL_GAUGE_PRESSURE=0x23

# Kraftstofftank-Inhalt
# -> Einheit: % => (100/255)*value
FUEL_TANK_LEVEL=0x2F

# Distanz seit Loeschung der Fehlercodes
# -> Einheit: km => (256*value+value
DISTANCE_TRAVEL_SINCE_CLEARDTCS=0x31

# Barometrischer Druck
# -> Einheit: kPa
BAROMETRIC_PRESSURE=0x33

# Totpunkt
# -> Hinweis: Es gibt einen unteren (=BDC = Bottom Dead Center) und einen oberen Totpunkt (= BTC = Before Top Center bzw. BTDC = Before Top Dead Center)
#             (hier wird der obere Totpunkt verwendet)
# -> Einheit: * before TDC (= TDC = Dead entre)  => (value/2)-64
#    (Wertebereich: -64* ... +63.5*)
TIMING_ADVANCE=0x0E

# Kurzzeit- und Langzeit- Einspritztrimmung
# -> Hinweis: die Kurzzeit-Einspritzung wird mit SFT (= Short Term Fuel Trim) und die Langzeit-Einspritzung mit LFT (= Long Term Fuel Trim) abgekuerzt
# -> Einheit: % (fuer SFT und LFT) => (100/128)*value-100
SHORT_TERM_FUEL_TRIM=0x06
LONG_TERM_FUEL_TRIM=0x07

# MAP-Sensor
# -> Hinweis: MAP steht fuer Manifold Absolute Pressure; es ist ein Drucksensor zur Erfassung des Saugrohr-Absolutdrucks bei Otto- und Turbodieselmotoren
#             (Abkuerzung: MAP; es wird der Einlasskanal Absolutdruck gemessen)
# -> Einheit: kPa
MANIFOLD_ABSOLUTE_PRESSURE=0x0B

# Oxygen Sensors Present
# -> Hinweis: Es ist die Lambdasonde, um den Sauerstoffgehalt waehrend der Verbrennung zu messen
OXYGEN_SENSORS_PRESENT=0x13

# Oxygen Sensor 1
# -> Einheit: V bzw. % => value/200 bzw. (100/128)*value-100
OXYGEN_SENSOR_1=0x15

# OBD Standards
OBD_STANDARDS=0x1C

# Supportes PIDs
Supported_PIDs_0_20=0x00
Supported_PIDs_21_40=0x20
Supported_PIDs_41_60=0x40
Supported_PIDs_61_80=0x60
Supported_PIDs_81_A0=0x80
Supported_PIDs_A1_C0=0xA0
Supported_PIDs_C1_E0=0xC0


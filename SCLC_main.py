import visa
import time
import time
import serial.tools.list_ports
import serial
ser = serial.Serial('COM5',9600,timeout=0)
rm = visa.ResourceManager()
print(rm.list_resources())
B2901A_address = rm.list_resources()[0]
SMU = rm.open_resource(B2901A_address)
print(SMU.query('*IDN?'))

stepTime = .01
points = 1000
Vmax = 10
Vmin = -Vmax
currProt = .125
totalTime = stepTime*points

time.sleep(0.5)
ser.write(b'+0')
time.sleep(2)
mux = 1
ser.write(str.encode('-'+str(mux)))
time.sleep(2)

# Sweep Up
SMU.write('*RST')
SMU.write(':SOUR:FUNC:MODE VOLT')
SMU.write(':SOUR:VOLT:MODE SWE')
SMU.write(':SOUR:VOLT:RANG 20')
SMU.write(':SOUR:VOLT:STAR 0')
SMU.write(':SOUR:VOLT:STOP {}'.format(Vmax))
SMU.write(':SOUR:VOLT:POIN {}'.format(points))
SMU.write(':SOUR:SWE:DIR UP')
SMU.write(':SOUR:SWE:SPAC LIN')
SMU.write(':SOUR:SWE:STA SING')
SMU.write(':SENS:FUNC ""CURR""')
SMU.write(':SENS:CURR:RANG:AUTO ON')
SMU.write(':SENS:CURR:APER {}'.format(stepTime))
SMU.write(':SENS:CURR:PROT {}'.format(currProt))
SMU.write(':FORM:DATA ASC')
SMU.write(':TRIG:SOUR AINT')
SMU.write(':TRIG:COUN {}'.format(points))
SMU.write(':OUTP ON')
SMU.write(':INIT (@1)')
time.sleep(totalTime + 1)

measCurr1 = SMU.query(':FETC:ARR:CURR? (@1)').split(',')
sourceVolts1 = SMU.query(':FETC:ARR:VOLT? (@1)').split(',')

# Sweep Down
SMU.write('*RST')
SMU.write(':SOUR:FUNC:MODE VOLT')
SMU.write(':SOUR:VOLT:MODE SWE')
SMU.write(':SOUR:VOLT:RANG AUTO')
SMU.write(':SOUR:VOLT:STAR 0')
SMU.write(':SOUR:VOLT:STOP {}'.format(Vmin))
SMU.write(':SOUR:VOLT:POIN {}'.format(points))
SMU.write(':SOUR:SWE:DIR UP')
SMU.write(':SOUR:SWE:SPAC LIN')
SMU.write(':SOUR:SWE:STA SING')
SMU.write(':SENS:FUNC ""CURR""')
SMU.write(':SENS:CURR:RANG:AUTO ON')
SMU.write(':SENS:CURR:APER {}'.format(stepTime))
SMU.write(':SENS:CURR:PROT {}'.format(currProt))
SMU.write(':TRIG:SOUR AINT')
SMU.write(':TRIG:COUN {}'.format(points))
SMU.write(':OUTP ON')
SMU.write(':INIT (@1)')
time.sleep(totalTime + 1)

measCurr2 = SMU.query(':FETC:ARR:CURR? (@1)').split(',')
sourceVolts2 = SMU.query(':FETC:ARR:VOLT? (@1)').split(',')

SMU.write(':OUTP OFF')

measCurr = measCurr1 + measCurr2
sourceVolts = sourceVolts1 + sourceVolts2

sourceVoltsFloat = [float(x) for x in sourceVolts]
measCurrFloat = [float(x) for x in measCurr]
print(sourceVoltsFloat)
print(measCurrFloat)
with open('M1Dh1TEST.csv','w',newline='') as csvfile:
    lis = [sourceVoltsFloat,measCurrFloat]
    csvfile.write("Voltage (V),Current (A)\n")
    for x in zip(*lis):
        csvfile.write("{0},{1}\n".format(*x))

SMU.close()

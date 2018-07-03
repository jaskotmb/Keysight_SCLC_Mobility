import visa
import time
import datetime
import serial.tools.list_ports
import serial
import csv
import os


def LinSweep(SMUName, Vbegin, Vend, samplePoints, stepT, maxCurr):
    totalTime = stepT * samplePoints
    SMU.write('*RST')
    SMU.write(':SOUR:FUNC:MODE VOLT')
    SMU.write(':SOUR:VOLT:MODE SWE')
    SMU.write(':SOUR:VOLT:RANG 20')
    SMU.write(':SOUR:VOLT:STAR {}'.format(Vbegin))
    SMU.write(':SOUR:VOLT:STOP {}'.format(Vend))
    SMU.write(':SOUR:VOLT:POIN {}'.format(samplePoints))
    SMU.write(':SOUR:SWE:DIR UP')
    SMU.write(':SOUR:SWE:SPAC LIN')
    SMU.write(':SOUR:SWE:STA SING')
    SMU.write(':SENS:FUNC ""CURR""')
    SMU.write(':SENS:CURR:RANG:AUTO ON')
    SMU.write(':SENS:CURR:APER {}'.format(stepT))
    SMU.write(':SENS:CURR:PROT {}'.format(maxCurr))
    SMU.write(':FORM:DATA ASC')
    SMU.write(':TRIG:SOUR AINT')
    SMU.write(':TRIG:COUN {}'.format(samplePoints))
    SMU.write(':OUTP ON')
    SMU.write(':INIT (@1)')
    time.sleep(totalTime + 2)
    measCurr = SMU.query(':FETC:ARR:CURR? (@1)').split(',')
    sourceVolts = SMU.query(':FETC:ARR:VOLT? (@1)').split(',')
    VIpairs = list(zip(sourceVolts,measCurr))
    return VIpairs

def stringTime():
    startTime = time.localtime()
    s = str(startTime.tm_year) + str(startTime.tm_mon).zfill(2) + str(startTime.tm_mday).zfill(2) + '-' + str(
        startTime.tm_hour).zfill(2) + '-' + str(startTime.tm_min).zfill(2) + '-' + str(startTime.tm_sec).zfill(2)
    return s

def makeTodayDir():
    todayName = stringTime()[0:8]
    if not os.path.exists(todayName):
        os.mkdir(todayName)
        print("Created Directory for today: {}\\{}".format(os.getcwd(),todayName))
    os.chdir(todayName)
    print("Changed Directory to: {}".format(os.getcwd()))
    return

# Opening serial communication to Arduino multiplexer switch
ser = serial.Serial('COM3', 9600, timeout=0)
# Opening connection to Keysight B2901A SMU
rm = visa.ResourceManager()
B2901A_address = rm.list_resources()[0]
SMU = rm.open_resource(B2901A_address)

# Creating / Navigating to the correct data directory (new one for each day)
os.chdir('C:\\Users\\Morty\\Documents\\Mobility_Data')
print("Current Directory: {}".format(os.getcwd()))
makeTodayDir()

# Initializing sweep parameters
timeStep = 0.1
numPoints = 1000
Vhi = 10
Vneg = -Vhi
currProt = 0.125
mux = [1,2,3,4,5,6,7,8]
each = ['V1','V2']
timeBegin = datetime.datetime.now()
elapse = 4*len(mux)*len(each)*(timeStep*numPoints+6.5)
timeEnd = timeBegin + datetime.timedelta(0,elapse)
print("Measurement Begin: {:%A, %d %B %Y %H:%M:%S}".format(timeBegin))
print("Measurement End:   {:%A, %d %B %Y %H:%M:%S}".format(timeEnd))

for i in mux:
    for k in each:
        sampleName = '180626Dh1'+str(i)+'-'+str(k)
        startTimeStr = stringTime()
        print("Time: {}, Sample: {} ".format(startTimeStr,sampleName),end='')

        # Initializing mux switch, selecting device
        time.sleep(0.5)
        ser.write(b'+0')
        time.sleep(2)
        ser.write(str.encode('-' + str(i)))
        time.sleep(2)

        x = LinSweep(SMU, 0, Vhi, numPoints, timeStep, currProt)
        y = LinSweep(SMU, Vhi, Vneg, numPoints*2, timeStep, currProt)
        z = LinSweep(SMU, Vneg, 0, numPoints, timeStep, currProt)
        totalVI = x + y + z

        outName = sampleName+'_'+startTimeStr
        with open('{}.csv'.format(outName), 'w',newline='') as csvfile:
            writer = csv.writer(csvfile)
            row1 = ["Voltage (V)","Current (A)"]
            writer.writerow(row1)
            for row in totalVI:
                writer.writerow(row)
        print("Data Saved")
SMU.write(':OUTP OFF')
SMU.close()

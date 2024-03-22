import datetime
import serial
import os
import subprocess
from multiprocessing import Process
from time import sleep
import time
from thermocouples_reference import thermocouples

result = 0
old_result = 0
ser = serial.Serial('/dev/ttyACM0')

Pv = 300
Iv = 30

P = 0
I = 0

dt = 1

max_val = 500

temp_err = 0
PI = 0



def clamp(n, min, max): 
    if n < min: 
        return min
    elif n > max: 
        return max
    else: 
        return n 

def getData():
    global old_result
    pro = subprocess.Popen(os.getcwd()+"/getData", shell=True, stdout=subprocess.PIPE)
    try:
        result = str(pro.communicate()[0]).split(" ")
    except:
        pro.kill()
        result = pro.communicate

    try:
        result = float(result[1])
        if result > 20 :
            result = 888
    except:
        result = 999
    try:
        result = typeK.inverse_CmV(result, Tref=25)
        old_result = result 
    except:
        result = old_result
    return(result)


def start():
    start  = str("Start Soldering process (Y/N): ")

    if (start != "Y" or start != "yes" or start != "YES"):
        start
        
def get_soll_temp(tim): #elapsed time
    if(tim <= 90):
        solltemp = 0.72 * tim + 25 #steigungs koeff * "genullte" Zeit + "anfangs" Temp
    elif(tim <= 180):
        solltemp = 0.44 * (tim - 90) + 90
    elif(tim <= 210):
        solltemp = 0.26 * (tim - 180) + 130
    elif(tim <= 240):
        solltemp = 0.9 * (tim - 210) + 138
    elif(tim <= 270):
        solltemp = -0.9 * (tim - 240) + 165
        
    return(solltemp)
    
def PID():
    elapsed_time = time.time() - starttime
    temp_err = get_soll_temp(elapsed_time) - getData()
    
    P = temp_err * Pv
    I += temp_err * Iv * dt
    
    PI = clamp(P + I, 0, elapsed_time) 
    
    
    print(getData + "," + PI)

start()
starttime = time.time()

i = 0

while(true):
    i += 1
    
    if(i == 4):
        PID()
    
    ser.write(b'1')
    sleep(0.25*(PI/max_val))
    ser.write(b'0')
    sleep(0.25*(1-(PI/max_val)))

    
   


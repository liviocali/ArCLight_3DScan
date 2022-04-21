import serial
import time, datetime
import argparse
import subprocess
import os
import numpy as np
import sys

# Open serial port
#s = serial.Serial('/dev/tty.usbserial-AG0K0EZI',115200)
usb_port = subprocess.check_output(['ls /dev/ttyUSB*'],shell=True).decode().strip()
s = serial.Serial(usb_port,115200)
print('Opening Serial Port')

newreadout = True #Set if new or  old readout used
tilesizex = 300
tilesizey = 280
ngridy = 14
stepsize = tilesizey/ngridy
monitorx = 180
monitory = 360
offsetx = 7.5 # Corner of the printerhead aligned with corner of the tile
offsety = 49.5 # Corner of the printerhead aligned with corner of the tile
offsetz = 185
data_path = '/data/LRS/acl_teststand/3dscan/data_files'
data_taking_time = 15 #wait time for one data run


def removeComment(string):
    if (string.find(';')==-1):
        return string
    else:
        return string[:string.index(';')]
 
def mycord():#You can enter specific place where you want to go 
    
    print('Enter coordinates');
    a = int(input('x coordinate between 34 and 334: \n'))
    while a < 34 or a > 334:
        print('The entered number is not allowed\n')
        a = int(input('x coordinate between 70 and 370: \n'))

    b = int(input('y coordinate between 33.5 and 333.5: \n'))
    while b < 33 or b > 333.5:
        print('The entered number is not allowed\n')
        b = int(input('y coordinate between 54 and 354: \n'))

    #c = input('z coordinate between 22 and 200: \n')
    #while c < 22 or b > 200:
        #print('The entered number is not allowed\n')
        #c = int(input('y coordinate between 22 and 200: \n'))

    gcode_file = open("cord.g","w")
    gcode_file.write('G0')
    gcode_file.write(" ")
    gcode_file.write('X')
    gcode_file.write(str(a))
    gcode_file.write(" ")
    gcode_file.write('Y')
    gcode_file.write(str(b))
    gcode_file.write(" ")
    gcode_file.write('Z')
    gcode_file.write('22')
    gcode_file.close()

def mytestseq():#Scan on the first line 

    f = open("testseq.g","w")
    a = 10
    b = 10

    while a<100:
        while b<100:
            a+=10
            b+=10
            f.write('G0')
            f.write(" ")
            f.write('X')
            f.write(str(a))
            f.write(" ")
            f.write('Y')
            f.write(str(b))
            f.write(" ")
            f.write('Z')
            f.write('0')
            f.write('\n')
    
    f.close()
        
def myseq(): #Whole scan of the entire tile with stop at each cm

    f = open("seq.g","w")
    stepsize = 10
    a = 33.5
    b = 43.5
    while a < 323.5 and b < 333.5:
        while a < 323.5:
            a += stepsize
            f.write('G0')
            f.write(" ")
            f.write('X')
            f.write(str(a))
            f.write(" ")
            f.write('Y')
            f.write(str(b))
            f.write(" ")
            f.write('Z')
            f.write('0')
            f.write('\n')

        a = 333.5
        b += stepsize
    
        while a > 43.5:
            a -= stepsize
            f.write('G0')
            f.write(" ")
            f.write('X')
            f.write(str(a))
            f.write(" ")
            f.write('Y')
            f.write(str(b))
            f.write(" ")
            f.write('Z')
            f.write('0')
            f.write('\n')

        a = 33.5
        b += stepsize

    f.close()
        
def mycodesender(mygcode):#Chose wich gcode file you want to send, first initialization (init.g), then sequence (only works when connected to printer)
    #mygcode = str(input('Enter the gcode file to be used (XYZ.g): \n'))
    # Open g-code file
    f = open(mygcode,'r');
    print('Opening gcode file')
 
    # Wake up 
    s.write(str.encode("\r\n\r\n")) # Hit enter a few times to wake the Printrbot
    time.sleep(2)   # Wait for Printrbot to initialize
    s.flushInput()  # Flush startup text in serial input
    print('Sending gcode')
    time.sleep(2)
 
    # Stream g-code
    for line in f:
    	l = removeComment(line)
    	l = l.strip() # Strip all EOL characters for streaming
    	if  (l.isspace()==False and len(l)>0) :
    		print('Sending: ' + l)
    		l = (l + '\n')
    		time.sleep(1)
    		s.write(l.encode()) # Send g-code block
    		time.sleep(1)
    		while s.in_waiting >0:
    			grbl_out = s.readline() # Wait for response with carriage return
    			grbl_out = grbl_out.decode()
    			print(' : ' + grbl_out.strip())


    #Close file
    f.close()
    time.sleep(3)
    while s.in_waiting >0:
    	grbl_out = s.readline() # Wait for response with carriage return
    	grbl_out = grbl_out.decode()
    	print(' : ' + grbl_out.strip())

def goto(x,y,z):
    mystring = 'G0 '+'X'+str(x)+' '+'Y'+str(y)+' '+'Z'+str(z)+'\n'
    s.write(mystring.encode()) # Send g-code block
    grbl_out = s.readline() # Wait for response with carriage return
    grbl_out = grbl_out.decode()
    print(' : ' + grbl_out.strip())#print the feedback

def startdaq():
    if newreadout:
        print("EchoStart")
        subprocess.call(["echo 1 > ~/.adc_watchdog_file"],shell=True)
        print("Echo1")
        #for i in range(20):
            #if subprocess.call(["cat ~/.adc_watchdog_file"],shell=True) == 1:
            #    print("Echo1")
            #    break
            #elif i == 19:
            #    sys.exit("Error in the turn on of the watchdog")
            #else:
            #    subprocess.call(["echo 1 > ~/.adc_watchdog_file"],shell=True)
        time.sleep(data_taking_time)
        subprocess.call(["echo 0 > ~/.adc_watchdog_file"],shell=True)
        print("Echo0")
        #for i in range(20):
        #    if subprocess.call(["cat ~/.adc_watchdog_file"],shell=True) == 0:
        #        print("Echo0")
        #        break
        #    elif i == 19:
        #    
        #        sys.exit("Error in the turn off of the watchdog")
        #    else:
        #        subprocess.call(["echo 0 > ~/.adc_watchdog_file"],shell=True)
        time.sleep(1)
        out = subprocess.check_output("ls "+data_path+"/0cd913fb_*.data -rt | tail -n 1 | tail -c 30",shell=True).decode().strip()
        time.sleep(1)

    else:
        f = open("/data/3dscan/mylog.log","w")
        subprocess.call(["/home/lhep/afi-adc64-without-watchdog/build/adc64-system/afi-adc64-system","--cli_mode","--data_dir","/data/3dscan","--event_number","15000"],stderr=f)
        out = subprocess.check_output("grep -a \"MStreamFileWriter opened file: /data/3dscan/\" /data/3dscan/mylog.log | tail -c 30",shell=True)[:-1].decode()
        while(not subprocess.call("grep \"AdcSelfTest failed\" /data/3dscan/mylog.log",shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)):
            os.remove("/data/3dscan/"+str(out))
            f.close()
            f = open("/data/3dscan/mylog.log","w")
            subprocess.call(["/home/lhep/afi-adc64-without-watchdog/build/adc64-system/afi-adc64-system","--cli_mode","--data_dir","/data/3dscan","--event_number","15000"],stderr=f)
            out = subprocess.check_output("grep -a \"MStreamFileWriter opened file: /data/3dscan/\" /data/3dscan/mylog.log | tail -c 30",shell=True)[:-1].decode()
    return out

def mymain():
    print("Start initialisation")
    #mycodesender("preinit.g")
    #time.sleep(10)
    mycodesender('init.g')
    print("Wait 30s")
    time.sleep(25)
    xmax = offsetx + tilesizex
    ymax = offsety + tilesizey
    xmin = offsetx
    x = offsetx+stepsize/2.
    y = offsety+stepsize/2.
    z = offsetz
    #goto(x,y,z)
    time.sleep(10)

    while s.in_waiting >0:
    	grbl_out = s.readline() # Wait for response with carriage return
    	grbl_out = grbl_out.decode()
    	print(' : ' + grbl_out.strip())

    print("Initialisation over\n Ready\n")
    input("Press Enter to start data taking")
    
    #make monitor run
    goto(180,180,offsetz)
    time.sleep(20)
    goto(monitorx,monitory,offsetz)
    time.sleep(20)
    mycodesender("stopmotor.g")
    time.sleep(2)
    filename = startdaq()
    writefile(monitorx,monitory,-99,filename)
    
    #start scan
    goto(x,y,z)
    time.sleep(10)
    stepcounter=0
    nsteps = (int(tilesizex/stepsize)) * (int(tilesizey/stepsize))
    while x < xmax and y < ymax:
        while x < xmax:
            stepcounter+=1
            print("Step X:"+str(x-offsetx)+' Y:'+str(y-offsety)+' Z:'+str(z)+' Step:'+str(stepcounter)+'/'+str(nsteps),end=" ")
            if stepcounter==1:
            	start_time = time.time()
            else:
            	print("Time remaining: "+time.strftime("%H:%M:%S",time.gmtime(steptime*(nsteps-stepcounter))))
            goto(x,y,z)
            print("Turning off motor for data taking")
            mycodesender("stopmotor.g")
            time.sleep(4)
            filename = startdaq()
            writefile(x,y,z,filename)
            x += stepsize
            if stepcounter==1:
            	end_time = time.time()
            	steptime = end_time-start_time
        x -= stepsize
        y += stepsize

        while x > xmin:
            stepcounter+=1 
            print("Step X:"+str(x-offsetx)+' Y:'+str(y-offsety)+' Z:'+str(z)+' Step:'+str(stepcounter)+'/'+str(nsteps),end=" ")
            print("Time remaining: "+time.strftime("%H:%M:%S",time.gmtime(steptime*(nsteps-stepcounter))))         
            goto(x,y,z)
            print("Turning off motor for data taking")
            mycodesender("stopmotor.g")
            time.sleep(4)
            filename = startdaq()
            writefile(x,y,z,filename)
            x -= stepsize
        x += stepsize
        y += stepsize
    
    #monitor run
    goto(180,180,offsetz)
    time.sleep(20)
    goto(monitorx,monitory,offsetz)
    time.sleep(20)
    mycodesender("stopmotor.g")
    time.sleep(4)
    filename = startdaq()
    writefile(monitorx,monitory,99,filename)
    
    print("Scan finished in "+time.strftime("%H:%M:%S",time.gmtime(time.time()-start_time)))    
    goto(300,300,200)

def writefile(x,y,z,filename):
    f = open("data_position.log","a")
    f.write(str(x-offsetx)+' '+str(y-offsety)+' '+str(z)+' '+filename+'\n')
    f.close()


if __name__=='__main__':
    mymain()





        

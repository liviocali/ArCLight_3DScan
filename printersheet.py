import serial
import time
import argparse
import subprocess

# Open serial port
s = serial.Serial('/dev/tty.usbserial-AG0K0EZI',115200)
#s = serial.Serial('/dev/ttyUSB0',115200)
print('Opening Serial Port')

tilesizex = 300
tilesizey = 280
stepsize = 10 
offsetx = 38 # Corner of the printerhead aligned with corner of the tile
offsety = 74 # Corner of the printerhead aligned with corner of the tile

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
    		grbl_out = s.readline() # Wait for response with carriage return
    		grbl_out = grbl_out.decode()
    		print(' : ' + grbl_out.strip())


    #Close file and serial port
    f.close()
    time_end = time.time() + 20
    while time.time()<time_end:
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
   f = open("/data/LRS/acl_teststand/3dscan/mylog.log","w")
   subprocess.call(["afi-adc64-system","--cli_mode","--data_dir","/data/LRS/acl_teststand/3dscan","--event_number","1000"],stderr=f)
    out = subprocess.check_output("grep \"MStreamFileWriter opened file: /data/LRS/acl_teststand/3dscan/\" /data/LRS/acl_teststand/3dscan/mylog.log | cut -c63-",shell=True)
    return out[:-1].decode()

def mymain():
    print("Start initialisation")
    mycodesender('init.g')
    #time.sleep(30)
    print("Initialisation over\n Ready\n")
    xmax = offsetx + tilesizex
    ymax = offsety + tilesizey
    xmin = offsetx
    x = offsetx+stepsize
    y = offsety+stepsize
    z = 20
    stepcounter=0
    nsteps = int((int(xmax-x)/int(stepsize)) * (int(ymax-y)/int(stepsize)))
    while x < xmax and y < ymax:
        while x < xmax:
            stepcounter+=1
            print("Step X:"+str(x-offsetx)+' Y:'+str(y-offsety)+' Z:'+str(z)+' Step:'+str(stepcounter)+'/'+str(nsteps))
            goto(x,y,z)
            #filename = startdaq()
            #writefile(x,y,z,filename)
            time.sleep(2)
            x += stepsize
        x = xmax - 10
        y += stepsize

        while x > xmin:
            stepcounter+=1 
            print("Step X:"+str(x-offsetx)+' Y:'+str(y-offsety)+' Z:'+str(z)+' Step:'+str(stepcounter)+'/'+str(nsteps))         
            goto(x,y,z)
            #filename = startdaq()
            #writefile(x,y,z,filename)
            time.sleep(2)
            x -= stepsize
        x = xmin + 10
        y += stepsize

def writefile(x,y,z,filename):
    f = open("data_position.log","a")
    f.write(str(x-offsetx)+' '+str(y-offsety)+' '+str(z)+' '+filename+'\n')
    f.close()


if __name__=='__main__':
    mymain()





        

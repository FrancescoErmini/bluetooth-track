#!/usr/bin/python

import subprocess
import re
import os, sys
import time, threading
import datetime
from gps3 import agps3
gpsd_socket = agps3.GPSDSocket()
data_stream = agps3.DataStream()
gpsd_socket.connect()
gpsd_socket.watch()

#Configure the connection with Android to retrive GPS data from blueNMEA. 
#run those two command only once. 
#def init():
#	os.system("adb forward tcp:4352 tcp:4352")
#	os.system("gpsd -b -n tcp://localhost:4352")

def trackBT():
	print("Start bluetooth discovering")
	#Create different log file for each scan session
	basename = "mylogfile"
	suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
	filename = "_".join([basename, suffix]) # e.g. 'mylogfile_120508_171442'
	myfile = open(filename,"w")
	#the script loop until press 'Ctrl+C'
	while 1:
		try:
			print "new scan"
			#Ubertooth-scan is used to retrive LAP and UAP of an undiscoverable BT MAC address.
			#After launch the command, parse the shell output to retrive UAP+LAP value
			p = subprocess.Popen(["ubertooth-scan", "-U 0 -b hci0 -x -t 40"],shell=True,stdout=subprocess.PIPE)
			out = p.stdout.read()
			#out = p.communicate()
			for line in out.split("\n"):
				print(line)
				try:
					#lap = re.search(r'\?\?\:\?\?\:(.*)', line).group(1) #LAP format is XX:XX:XX
					regObj = re.search(r'(\sLAP\=(.*?)\s)(.*)(\ss\=(.*?)\s)', line)
					lap = regObj.group(2)
					s = regObj.group(5)
					s_num = re.sub(r'(?i)\-+','',s)
					#lapHEX = re.sub(r'(?i)\:+','',lap)  #LAP format is xxxxxx
			       		#uap = re.search(r'UAP\s*=\s*(.*)', line).group(1)
					#s = re.search(r"\ss\=(.*?)\s", line).group(1)
					n = int(s_num)
					if lap is not None and n < 65:
							#print "yess is numebr"
						#except ValueError:
						#11	print "not a number"
						print "found a close BT device"
						print ('MAC = ', lap)
						print  ('Signal =', s)
						print('signal num =', s_num)
						#Use gps3 python library to query gpsd
						for new_data in gpsd_socket:
		    					if new_data:
								data_stream.unpack(new_data)
								if data_stream.lon != 'n/a' and  data_stream.lat != 'n/a':
									longitude = data_stream.lon
									latitude = data_stream.lat
									print('Longitudine = ', data_stream.lon)
									print('Latitude = ', data_stream.lat)
									break
						t = raw_input("Enter track note:")
						#Report the value founded in the log file 
						print "log data into file"
						myfile.write("MAC: " + str(lap))
						myfile.write(" Signal " + str(s))
						myfile.write(" LONG: " + str(longitude))
						myfile.write(" LAT: " + str(latitude))
						myfile.write(" Note: " + str(t))
						myfile.write("\n\n")
				except AttributeError:
					print ''
			#p.stdout.close()
		#	time.sleep(10)

		except KeyboardInterrupt:
			myfile.close()
			os.system("ubertooth-util -r")
			sys.exit("quit scan")





trackBT()
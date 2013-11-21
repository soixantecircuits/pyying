from OSC import *   #required, to install : sudo pip install pyOSC
from time import sleep
listen_address = '127.0.0.1'
port = 6666
c = OSCClient()
c.connect((listen_address, port))	# connect to our OSCServer
bundle = OSCBundle("/pyying/shoot")
#bundle.setTimeTag(time.time() + 5)
bundle.append ("1")
while True:
	c.send(bundle)
	sleep(30)
	#sleep(1)

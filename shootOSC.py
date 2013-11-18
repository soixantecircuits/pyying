from OSC import *   #required, to install : sudo pip install pyOSC

listen_address = '127.0.0.1'
port = 6666
c = OSCClient()
c.connect((listen_address, port))	# connect to our OSCServer
bundle = OSCBundle("/pyying/shoot")
#bundle.setTimeTag(time.time() + 5)
bundle.append ("1")
c.send(bundle)

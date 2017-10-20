import pexpect

child = pexpect.spawn('gphoto2 --shell --filename /home/pi/camera/photo-%Y%m%d-%H%M%S.jpg')
child.expect('gphoto2: {/opt/bin/pyying} />')
child.sendline('capture-image-and-download')
child.expect('gphoto2: {/opt/bin/pyying} />')
print child.before 
child.sendline('capture-image-and-download')
child.expect('gphoto2: {/opt/bin/pyying} />')
print child.before 

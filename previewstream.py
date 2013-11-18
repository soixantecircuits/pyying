#to run a mjpeg server (like IP camera)
# run $ mjpg_streamer -i "/usr/local/lib/input_file.so -r -f /tmp/stream" -o "/usr/local/lib/output_http.so -w /usr/local/www -p 8080"



import piggyphoto, pygame
import os
import time
from OSC import *   #required, to instll : sudo pip install python-osc


def quit_pressed():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
    return False

def show(file):
    picture = pygame.image.load(file)
    main_surface.blit(picture, (0, 0))
    pygame.display.flip()

def printing_handler(addr, tags, stuff, source):
    msg_string = "%s [%s] %s" % (addr, tags, str(stuff))
    sys.stdout.write("OSCServer Got: '%s' from %s\n" % (msg_string, getUrlStr(source)))
    return

def stream_handler(addr, tags, data, client):
    print "Stream: " + str(data) + " is that " + str(True) + " ?"
    global isStreaming
    isStreaming = data
    return

def shoot_handler(addr, tags, data, client):
    print 'Shoot!'
    global isShooting
    isShooting = True
    return

s = OSCServer(('localhost', 6666))
s.addDefaultHandlers()
s.addMsgHandler("default", printing_handler)
s.addMsgHandler("/pyying/stream", stream_handler)
s.addMsgHandler("/pyying/shoot", shoot_handler)
st = threading.Thread(target=s.serve_forever)
st.start()
print "Starting OSCServer. Use ctrl-C to quit."

path = '/tmp/stream/'
filename = 'preview'
extension = 'jpg'
number = 0
snap_number = 0
fullpath = path + filename + str(number) + '.' + extension

clock = pygame.time.Clock()
try:
  C = piggyphoto.camera()
  C.leave_locked()
  C.capture_preview(fullpath)

  picture = pygame.image.load(fullpath)
  pygame.display.set_mode(picture.get_size())
  main_surface = pygame.display.get_surface()

  isStreaming = True
  isShooting = False

  oldtime = time.time()
  while not quit_pressed():
    print str(clock.get_fps())
    clock.tick(25)
    if (isShooting):
      isShooting = False
      C.capture_image('snap' + str(snap_number) + '.jpg')
      snap_number+=1
    if (isStreaming):
        fullpath = path + filename + str(number) + '.' + extension
        C.capture_preview(fullpath)
        show(fullpath)
        number += 1
except KeyboardInterrupt:
  pass
except Exception as e:
  print str(e) 
  pass

# close    
s.close()
st.join()

#to run a mjpeg server (like IP camera)
# run $ mjpg_streamer -i "/usr/local/lib/input_file.so -r -f /tmp/stream" -o "/usr/local/lib/output_http.so -w /usr/local/www -p 8080"

from socketIO_client import SocketIO #required, to install : sudo pip install -U socketIO-client
import logging
logging.basicConfig(level=logging.DEBUG) # debug only

import threading
import piggyphoto, pygame
import os
import sys
import time
import glob
import getopt
import signal

class Pyying():
    snap_path = os.path.dirname(__file__) + '/snaps/'
    snap_filename = 'snap'
    path = '/tmp/stream/'
    filename = 'preview'
    extension = 'jpg'
    number = 0
    snap_number = 0

    oscServer = None
    oscThread = None
    main_surface = None
    nowindow = False

    isStreaming = True
    isShooting = False

    def __init__(self, host="127.0.0.1", port=8010, nowindow=False):
        self.nowindow = nowindow
        self.host = host
        self.port = port

        # socket.io
        self.thread_socket = threading.Thread(None, self.socket_handler, None)
        print "Starting. Use ctrl-C to quit."

        try:
          # check folders exist
          if not os.path.exists(self.path):
                os.makedirs(self.path)
          if not os.path.exists(self.snap_path):
                os.makedirs(self.snap_path)
          self.find_last_number_in_directory()

          # camera
          self.camera = piggyphoto.camera()
          self.camera.leave_locked()
          fullpath = self.path + self.filename + ("%05d" % self.number) + '.' + self.extension
          self.camera.capture_preview(fullpath)

          # create window from first preview
          if (not self.nowindow):
            picture = pygame.image.load(fullpath)
            pygame.display.set_mode(picture.get_size())
            self.main_surface = pygame.display.get_surface()
        except KeyboardInterrupt:
          self.close()
        except Exception as e:
          print str(e)
          self.close()

    def start(self):
        self.thread_socket.start()
        clock = pygame.time.Clock()
        try:
          while not self.quit_pressed():

            # trying to get a fixed fps. However the camera is limiting to approx 22 fps
            # print str(clock.get_fps())
            clock.tick(25)

            # Shoot picture
            if (self.isShooting):
              self.isShooting = False
              print 'Shoot!'
              fullpath = self.snap_path + self.snap_filename + ("%05d" % self.snap_number) + '.' + self.extension
              self.camera.capture_image(fullpath, delete=True)
              self.snap_number+=1

            # Stream pictures
            if (self.isStreaming):
                fullpath = self.path + self.filename + str(self.number) + '.' + self.extension
                self.camera.capture_preview(fullpath)
                if (not self.nowindow):
                  self.show(fullpath)
                self.number += 1

          self.close()

        except KeyboardInterrupt:
          self.close()
        except Exception as e:
          print str(e)
          self.close()

    def socket_handler(self):
      self.socket = SocketIO(self.host, self.port)
      self.socket.on('shoot', self.pong)
      self.socket.wait()

    def pong(data):
      print 'pong'

    def close(self):
        self.thread_socket._Thread__stop()
        self.camera.leave_locked()

    def quit_pressed(self):
      if (not self.nowindow):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN :
              if event.key == pygame.K_SPACE :
                self.isShooting = True
      return False

    def show(self,file):
        try:
          picture = pygame.image.load(file)
          self.main_surface.blit(picture, (0, 0))
          pygame.display.flip()
        except Exception as e:
          print str(e)

    def stream_handler(self, addr, tags, data, client):
        print "Stream: " + str(data) + " is that " + str(True) + " ?"
        self.isStreaming = data
        return

    def shoot_handler(self):
        self.isShooting = True
        return

    def find_last_number_in_directory(self):
        fullpath = self.snap_path + self.snap_filename + '*.' + self.extension
        files = sorted(glob.glob(fullpath))
        if (len(files) > 0):
          filename = files[-1]
          regex = re.compile(r'\d\d\d\d\d')
          number = regex.findall(filename)
          if (len(number) > 0):
            self.snap_number = int(number[0]) + 1

        return


def main(argv):
  nowindow = False

  try:
    opts, args = getopt.getopt(argv,"hn",["nowindow"])
  except getopt.GetoptError:
    print 'pyying.py -h to get help'
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'press spacebar to take a snapshot'
      print 'run "pyying.py --nowindow" for a x-less run'
      sys.exit()
    elif opt in ("-n", "--nowindow"):
        nowindow = True

  ying = Pyying(nowindow=nowindow)
  ying.start()

if __name__ == '__main__':
	main(sys.argv[1:])

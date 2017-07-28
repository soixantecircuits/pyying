#to run a mjpeg server (like IP camera)
# run $ mjpg_streamer -i "/usr/local/lib/input_file.so -r -f /tmp/stream" -o "/usr/local/lib/output_http.so -w /usr/local/www -p 8080"


import threading
import piggyphoto
import os
import sys
import time
import glob
import getopt
import signal
import re
import signal
from OSC import * #required, to install : sudo pip install pyOSC
from dotmap import DotMap
import pyStandardSettings
from pyStandardSettings import settings

class Pyying():
    snap_path = 'snaps' # Don't forget to $ chown `whoami` this folder
    snap_filename = 'snap'
    stream_path = '/tmp/stream'
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
    isClosing = False

    def __init__(self, host="localhost", port=8010, nowindow=False):
        self.nowindow = nowindow
        self.host = host
        self.port = port
        self.settings = DotMap(pyStandardSettings.getSettings())
        self.snap_path = str(self.settings.folder.output)
        self.stream_path = str(self.settings.folder.stream)

        # osc
        self.oscServer = OSCServer((host, int(port)))
        self.oscServer.addDefaultHandlers()
        self.oscServer.addMsgHandler("/pyying/stream", self.stream_handler)
        self.oscServer.addMsgHandler("/pyying/shoot", self.shoot_handler)
        self.oscThread = threading.Thread(target=self.oscServer.serve_forever)
        self.oscThread.start()
        print "Starting OSCServer. Use ctrl-C to quit."


        # TERM
        signal.signal(signal.SIGTERM, self.sigclose)

        try:
          # check folders exist
          if not os.path.exists(self.stream_path):
                os.makedirs(self.stream_path)
          if not os.path.exists(self.snap_path):
                os.makedirs(self.snap_path)
          self.find_last_number_in_directory()

          # camera
          self.camera = piggyphoto.camera()
          self.camera.leave_locked()
          fullpath = os.path.join(self.stream_path, self.filename + ("%05d" % self.number) + '.' + self.extension)
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
        if (not self.nowindow):
          clock = pygame.time.Clock()
        try:
          while not self.quit_pressed():

            # trying to get a fixed fps. However the camera is limiting to approx 22 fps
            # print str(clock.get_fps())
            if (not self.nowindow):
              clock.tick(25)

            # Shoot picture
            if (self.isShooting):
              self.isShooting = False
              print 'Shoot!'
              fullpath = os.path.join(self.snap_path, self.snap_filename + ("%05d" % self.snap_number) + '.' + self.extension)
              self.camera.capture_image(fullpath, delete=True)
              self.snap_number+=1

            # Stream pictures
            if (self.isStreaming):
                fullpath = os.path.join(self.stream_path, self.filename + str(self.number) + '.' + self.extension)
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


    def sigclose(self, signum, frame):
      self.isClosing = True

    def close(self):
        self.isClosing = True
        self.oscServer.close()
        self.oscThread.join()
        self.camera.leave_locked()
        print "Have a good day!"

    def quit_pressed(self):
      if (not self.nowindow):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN :
              if event.key == pygame.K_SPACE :
                self.isShooting = True
      return self.isClosing

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

    def shoot_handler(self, addr, tags, data, client):
        print "shoot"
        self.isShooting = True
        return

    def find_last_number_in_directory(self):
        fullpath = os.path.join(self.snap_path, self.snap_filename + '*.' + self.extension)
        files = sorted(glob.glob(fullpath))
        if (len(files) > 0):
          filename = files[-1]
          regex = re.compile(r'\d\d\d\d\d')
          number = regex.findall(filename)
          if (len(number) > 0):
            self.snap_number = int(number[0]) + 1

        return


def main(argv):
  settings = DotMap(pyStandardSettings.getSettings())
  if (not settings.nowindow):
    import pygame
  ying = Pyying(host=settings.server.host, port=settings.server.port, nowindow=settings.nowindow)
  ying.start()

if __name__ == '__main__':
	main(sys.argv[1:])

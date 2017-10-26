#to run a mjpeg server (like IP camera)
# run $ mjpg_streamer -i "/usr/local/lib/input_file.so -r -f /tmp/stream" -o "/usr/local/lib/output_http.so -w /usr/local/www -p 8080"

# TODO
# * get first ip from system if settings.server.host is ""
# * set standard port
# * do not use OSC if pyOSC not installed

from threading import Thread, Lock
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
from pySpacebroClient import SpacebroClient
from socketIO_client_nexus.exceptions import ConnectionError
from RootedHTTPServer import RootedHTTPServer, RootedHTTPRequestHandler

mutex = Lock()

class Pyying():
    snap_path = 'snaps' # Don't forget to $ chown `whoami` this folder
    snap_filename = 'snap'
    snap_extension = 'jpg'
    stream_path = '/tmp/stream'
    stream_filename = 'preview'
    stream_extension = 'jpg'
    number = 0
    snap_number = 0
    media = {}

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
        self.isStreaming = self.settings.streamAtStartup

        # osc
        self.oscServer = OSCServer((host, int(port)))
        self.oscServer.addDefaultHandlers()
        self.oscServer.addMsgHandler("/pyying/stream", self.stream_handler)
        self.oscServer.addMsgHandler("/pyying/shoot", self.shoot_handler)
        self.oscThread = Thread(target=self.oscServer.serve_forever)
        self.oscThread.start()
        print("Starting OSCServer. Use ctrl-C to quit.")

        # static file server
        self.staticFileServerThread = Thread(target=self.startStaticFileServer)
        self.staticFileServerThread.start()

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
          self.camera = piggyphoto.camera(False)
          if settings.camera.port:
              settings.camera.port = str(settings.camera.port)
          elif settings.camera.devpath:
              try:
                  import pyudev
                  context = pyudev.Context()
                  device = pyudev.Devices.from_path(context, str(settings.camera.devpath))
                  settings.camera.port = 'usb:{0},{1}'.format(device['BUSNUM'], device['DEVNUM'])
              except pyudev.device._errors.DeviceNotFoundAtPathError as e:
                  print('devpath not found', settings.camera.devpath)
                  self.quit()
          self.camera.init(settings.camera.port)
          self.camera.leave_locked()
          fullpath = self.getStreamPath()
          self.camera.capture_image(fullpath, delete=True)
          
          # spacebro
          self.spacebroThread = Thread(target=self.startSpacebroClient)
          self.spacebroThread.start()
          # self.sendStatus()


          # create window from first preview
          if (not self.nowindow):
            picture = pygame.image.load(fullpath)
            pygame.display.set_mode(picture.get_size())
            self.main_surface = pygame.display.get_surface()
        except KeyboardInterrupt:
          self.close()
        except Exception as e:
          print(str(e))
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

            # repeat shoot
            if (self.settings.interval):
              r, s = divmod(time.time(), self.settings.interval) 
              if (s < 0.01):
                self.isShooting = True
                self.media = {}
                self.media['albumId'] = str(r)

            # Shoot picture
            if (self.isShooting):
              self.isShooting = False
              self.shoot()
            # Stream pictures
            if (self.isStreaming):
                fullpath = self.getStreamPath()
                self.camera.capture_preview(fullpath)
                if (not self.nowindow):
                  self.show(fullpath)
                self.number += 1
            else:
              time.sleep(0.0001) # avoid cpu > 100%

          self.close()

        except KeyboardInterrupt:
          self.close()
        except Exception as e:
          print(str(e))
          self.close()

    def checkLibGphoto2Error(self, e):
      print(e)
      if e.result is -1:
        self.quit()

    def shoot(self):
      #print('Shoot received! ', time.time())
      if 'albumId' in self.media:
        fullpath = self.getSnapPath(self.media['albumId'], str(self.settings.cameraNumber))
      else:
        fullpath = self.getSnapPath()

      print('Shoot command! ', time.time())
      mutex.acquire()
      try:
        self.camera.capture_image(fullpath, delete=True)
      except piggyphoto.libgphoto2error as e:
        self.checkLibGphoto2Error(e)
      finally:
        time.sleep(1.5) # the firmware generates error if we ask for settings again too quickly
        mutex.release()
      print('Shoot finished! ', time.time())

      # say it on spacebro
      self.media['path'] = os.path.abspath(fullpath)
      self.media['file'] = os.path.basename(fullpath)
      self.media['url'] = "http://" + self.settings.server.host + ":" + str(self.settings.server.port) \
                        + "/" + self.media['file']
      self.media['cameraNumber'] = self.settings.cameraNumber
      spacebroSettings = self.settings.service.spacebro
      self.spacebroClient.emit(spacebroSettings.client['out'].outMedia.eventName, self.media)

      # clear
      self.media = {}

    def startSpacebroClient(self):
      spacebroSettings = self.settings.service.spacebro
      while not self.quit_pressed():
        try:
          self.spacebroClient = SpacebroClient(spacebroSettings.toDict(), wait_for_connection=False)
          self.spacebroClient.on(spacebroSettings.client['in'].shoot.eventName, self.onShoot)
          self.spacebroClient.on(spacebroSettings.client['in'].getConfig.eventName, self.onGetConfig)
          self.spacebroClient.on(spacebroSettings.client['in'].setConfig.eventName, self.onSetConfig)
          self.spacebroClient.on(spacebroSettings.client['in'].getStatus.eventName, self.onGetStatus)
          self.spacebroClient.on(spacebroSettings.client['in'].setInterval.eventName, self.onSetInterval)
          self.sendStatus()
          while not self.quit_pressed():
            self.spacebroClient.wait(3)
        except ConnectionError as e:
          print(str(e))
        time.sleep(1)
      if hasattr(self, 'spacebroClient'):
        self.spacebroClient.disconnect()
      return

    def startStaticFileServer(self):
      server_address = ('', self.settings['server']['port'])
      self.httpd = RootedHTTPServer(self.settings['folder']['output'], server_address, RootedHTTPRequestHandler)

      sa = self.httpd.socket.getsockname()
      if str(self.settings.server.host) is "":
        self.settings.server.host = sa[0]
      print("Serving folder '" + self.settings.folder.output + "' on " + self.settings.server.host + ":" + str(sa[1]) + " ...")
      self.httpd.serve_forever()

    def sigclose(self, signum, frame):
      self.quit()

    def quit(self):
      self.isClosing = True

    def close(self):
        print("Closing application")
        self.isClosing = True
        self.oscServer.close()
        self.oscThread.join()
        if hasattr(self, 'spacebroThread'):
          self.spacebroThread.join()
        self.httpd.shutdown()
        self.staticFileServerThread.join()
        try:
          self.camera.leave_locked()
        except AttributeError:
          pass
        print("Have a good day!")

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
          print(str(e))

    def stream_handler(self, addr, tags, data, client):
        print("Stream: " + str(data) + " is that " + str(True) + " ?")
        self.isStreaming = data
        return

    def shoot_handler(self, addr, tags, data, client):
        print("osc shoot")
        self.isShooting = True
        return

    def onShoot(self, data):
        print("spacebro shoot")
        self.media = data
        # self.isShooting = True
        self.shoot()
        return

    def onGetStatus(self, data):
        self.sendStatus()

    def onSetInterval(self, data):
        self.settings.interval = data["interval"]

    def sendStatus(self, error = 0):
        print("spacebro get status")
        data = {}
        data['cameraNumber'] = self.settings.cameraNumber
        data['stream'] = str(self.settings.service.mjpg_streamer.url)
        data['connected'] = self.camera.initialized
        data['lastError'] = str(error)
        spacebroSettings = self.settings.service.spacebro
        self.spacebroClient.emit(spacebroSettings.client['out'].status.eventName, data)
        return

    def onGetConfig(self, data):
        print("___________________")
        print("spacebro get config")
        currentIsStreaming = self.isStreaming
        self.isStreaming = False
        cfgmap = False
        retries = 100
        #retries = 0
        for i in range(1 + retries):
          mutex.acquire()
          print("ask firmware the config")
          try:
            cfgmap = self.camera.get_map_config()
            break
          except piggyphoto.libgphoto2error as e:
            self.checkLibGphoto2Error(e)
            if e.result is -1:
              break
          finally:
            time.sleep(2) # the firmware generates error if we ask for settings again too quickly
            mutex.release()
          time.sleep(0.01)
        self.isStreaming = True
        print('finished get config')

        self.isStreaming = currentIsStreaming
        if cfgmap:
          cfgmap['cameraNumber'] = self.settings.cameraNumber
          cfgmap['stream'] = str(self.settings.service.mjpg_streamer.url)
        spacebroSettings = self.settings.service.spacebro
        self.spacebroClient.emit(spacebroSettings.client['out'].config.eventName, cfgmap)
        return

    def onSetConfig(self, data):
        #print("spacebro set config", data)
        print("spacebro set config")
        #self.onGetConfig(0)
        currentIsStreaming = self.isStreaming
        self.isStreaming = False
        
        cfgmap = data
        cfgmap.pop('cameraNumber')
        cfgmap.pop('stream')
        cfgmap.pop('_to')
        cfgmap.pop('_from')
        retries = 100
        for i in range(1 + retries):
          mutex.acquire()
          try:
            self.camera.set_map_config(cfgmap)
            break
          except piggyphoto.libgphoto2error as e:
            self.checkLibGphoto2Error(e)
            if e.result is -1:
              break
          finally:
            time.sleep(2) # the firmware generates error if we set settings again too quickly
            mutex.release()
          time.sleep(0.01)
        print('finished set config')
        self.isStreaming = currentIsStreaming
        self.onGetConfig(data)

    def getStreamPath(self):
      fullpath = os.path.join(self.stream_path, self.stream_filename + ("%05d" % self.number) + '.' + self.stream_extension)
      return fullpath

    def getSnapPath(self, albumId=-1, cameraNumber='01'):
      if albumId is -1:
        albumId = ("%05d" % self.snap_number)
        self.snap_number+=1

      fullpath = os.path.join(self.snap_path, self.snap_filename + '-' + albumId  + '-' + cameraNumber + '.' + self.snap_extension)
      return str(fullpath)

    def find_last_number_in_directory(self):
        fullpath = os.path.join(self.snap_path, self.snap_filename + '-[0-9]*[0-9]*-*.' + self.snap_extension)
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

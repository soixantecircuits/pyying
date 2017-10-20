import piggyphoto
from dotmap import DotMap
import pyStandardSettings
import signal

isClosing = False
settings = DotMap(pyStandardSettings.getSettings())
fullpath = "capt0000.jpg"
camera = piggyphoto.camera(False)
print("Opening " + str(settings.camera.port))
camera.init(str(settings.camera.port))

def sigclose(self, signum, frame):
  global isClosing
  isClosing = True
signal.signal(signal.SIGTERM, sigclose)

try:
  while not isClosing:
    raw_input('gphoto2: {/opt/bin/pyying} />')
    camera.capture_image(fullpath, delete=True)
    print("Saving file as /opt/share/snaps/snap-02-20171019-190445.jpg")
except KeyboardInterrupt:
  print('interrupted!')


from dotmap import DotMap
import pyStandardSettings
from pyStandardSettings import settings
from pySpacebroClient import SpacebroClient
import sys

spacebroSettings = settings.service.spacebro
spacebroSettings.client.name = 'test-pyying'
spacebroClient = SpacebroClient(spacebroSettings.toDict())
spacebroClient.wait(1)
data = {}
data["interval"] = 15
if settings.interval is not False:
  print settings.interval
  data["interval"] = settings.interval
spacebroClient.emit(spacebroSettings.client['in'].setInterval.eventName, data)
spacebroClient.wait(3)

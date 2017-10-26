from dotmap import DotMap
import pyStandardSettings
from pyStandardSettings import settings
from pySpacebroClient import SpacebroClient

spacebroSettings = settings.service.spacebro
spacebroSettings.client.name = 'test-pyying'
spacebroClient = SpacebroClient(spacebroSettings.toDict())
spacebroClient.wait(1)
#spacebroClient.emit(spacebroSettings.client['in'].shoot.eventName, {"albumId": "myAlbumId"})
spacebroClient.emit(spacebroSettings.client['in'].getConfig.eventName, {})
def onConfig(data):
  retries = 10
  for i in range(1 + retries):
    spacebroClient.emit(spacebroSettings.client['in'].setConfig.eventName, data)
spacebroClient.on(spacebroSettings.client['out'].config.eventName, onConfig)
spacebroClient.wait(3)

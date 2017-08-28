#!/usr/bin/env python

# TODO
# * test if url returned after shoot does not return 404
# * run pyying from here

import unittest
import sys, os
from os import path
from mock import patch
from pySpacebroClient import SpacebroClient
import pyStandardSettings
from dotmap import DotMap

timeout=1
shoot_timeout=6
verbose=True

class TestSpacebroClient(unittest.TestCase):

    def on_inMedia(self, args):
        self.inMediaValue = args

    def test_shoot(self):
        settings = DotMap(pyStandardSettings.getSettings())
        spacebroSettings = settings.service.spacebro
        media = DotMap({
            'albumId': 'myAlbumId',
        })
        spacebroSettings.clientName = "pyying-test"
        spacebroClient = SpacebroClient(spacebroSettings.toDict())

        # Listen
        spacebroClient.on(str(spacebroSettings.client['out'].outMedia.eventName), self.on_inMedia)
        spacebroClient.wait(seconds=timeout)
        spacebroClient.emit(str(spacebroSettings.client['in'].shoot.eventName), media.toDict())
        spacebroClient.wait(seconds=shoot_timeout)

        self.assertEqual(DotMap(self.inMediaValue).albumId, media.albumId)
        self.assertTrue(path.exists(str(self.inMediaValue['path'])))
        spacebroClient.disconnect()



if __name__ == '__main__':
    unittest.main()

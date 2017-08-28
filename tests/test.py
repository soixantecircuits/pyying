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

timeout=2
shoot_timeout=6
verbose=True

class TestSpacebroClient(unittest.TestCase):

    def on_inMedia(self, args):
        self.inMediaValue = args

    def on_inConfig(self, args):
        self.config = args

    def test_config(self):
        settings = DotMap(pyStandardSettings.getSettings())
        spacebroSettings = settings.service.spacebro
        spacebroSettings.clientName = "pyying-test"
        spacebroClient = SpacebroClient(spacebroSettings.toDict())

        # Listen
        spacebroClient.on(str(spacebroSettings.client['out'].config.eventName), self.on_inConfig)
        spacebroClient.wait(seconds=timeout)
        spacebroClient.emit(str(spacebroSettings.client['in'].getConfig.eventName), {})
        spacebroClient.wait(seconds=timeout)

        print self.config
        # test good format
        self.assertEqual(self.config['main']['capturesettings']['aperture']['label'], 'Aperture')

        # test change value
        self.config['main']['capturesettings']['aperture']['value'] = '7.1'
        spacebroClient.emit(str(spacebroSettings.client['in'].setConfig.eventName), self.config)
        spacebroClient.wait(seconds=timeout)
        self.config = {}
        spacebroClient.emit(str(spacebroSettings.client['in'].getConfig.eventName), {})
        spacebroClient.wait(seconds=timeout)
        self.assertEqual(self.config['main']['capturesettings']['aperture']['value'], '7.1')

        # test change value again
        self.config['main']['capturesettings']['aperture']['value'] = '6.3'
        spacebroClient.emit(str(spacebroSettings.client['in'].setConfig.eventName), self.config)
        spacebroClient.wait(seconds=timeout)
        self.config = {}
        spacebroClient.emit(str(spacebroSettings.client['in'].getConfig.eventName), {})
        spacebroClient.wait(seconds=timeout)
        self.assertEqual(self.config['main']['capturesettings']['aperture']['value'], '6.3')

        spacebroClient.disconnect()


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

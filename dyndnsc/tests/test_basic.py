# -*- coding: utf-8 -*-

import unittest

import dyndnsc


class TestDynDnsc(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test_dyndnsc_factory(self):
        # the type of these exceptions is not formally required,
        # but we want to have some basic form of argument validity checking
        self.assertRaises(TypeError, dyndnsc.getDynDnsClientForConfig, None)
        self.assertRaises(KeyError, dyndnsc.getDynDnsClientForConfig, {})
        self.assertRaises(ValueError, dyndnsc.getDynDnsClientForConfig,
                          {'updaters': ()})

        # create a dummy config:
        config = {}
        config['detector'] = ("random", {})
        config['updaters'] = (("dummy", {'hostname': "example.com"}),)
        dyndnsclient = dyndnsc.getDynDnsClientForConfig(config)
        self.assertEqual(dyndnsclient.detector.af(), dyndnsclient.dns.af())
        self.assertTrue(dyndnsclient.needs_check())
        dyndnsclient.needs_forced_check()
        dyndnsclient.check()
        dyndnsclient.sync()
        dyndnsclient.has_state_changed()

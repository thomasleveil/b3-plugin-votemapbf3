# -*- encoding: utf-8 -*-
import logging
import os
from b3.config import CfgConfigParser

from tests import Bf3TestCase
from votemap import VotemapPlugin
from votemap.map import get_n_next_maps, get_n_random_maps


class ConfTestCase(Bf3TestCase):
    def setUp(self):
        Bf3TestCase.setUp(self)
        self.conf = CfgConfigParser()
        self.p = VotemapPlugin(self.console, self.conf)
        logger = logging.getLogger('output')
        logger.setLevel(logging.INFO)


class Test_default_conf(ConfTestCase):
    def setUp(self):
        ConfTestCase.setUp(self)
        self.conf.load(os.path.join(os.path.dirname(__file__), '../extplugins/conf/plugin_votemap.ini'))
        self.p.onLoadConfig()

    def test_command_cancelvote(self):
        self.assertEqual(20, self.p.config.getint('commands', 'cancelvote-cv'))
        self.p.onStartup()
        self.assertIn('cancelvote', self.adminPlugin._commands)
        cmd = self.adminPlugin._commands['cancelvote']
        self.assertTupleEqual((20, 100), cmd.level)
        self.assertEqual('cv', cmd.alias)

    def test_command_votemap(self):
        self.assertEqual(0, self.p.config.getint('commands', 'votemap'))
        self.p.onStartup()
        self.assertIn('votemap', self.adminPlugin._commands)
        cmd = self.adminPlugin._commands['votemap']
        self.assertTupleEqual((0, 100), cmd.level)
        self.assertEqual('', cmd.alias)

    def test_preferences(self):
        self.assertEqual(5, self.p.vote_interval)
        self.assertEqual(120, self.p.nextmap_display_interval)
        self.assertEqual(4, self.p.vote_duration)
        self.assertEqual(0, self.p.vote_threshold)
        self.assertEqual(4, self.p.number_of_vote_options)
        self.assertEqual(True, self.p.exclude_current_map)
        self.assertEqual(True, self.p.exclude_next_map)
        self.assertEqual(get_n_next_maps, self.p.map_options_pickup_strategy)


class Test_pickup_strategies(ConfTestCase):
    def test_sequential(self):
        self.conf.loadFromString("""
[preferences]
map_options_pickup_strategy: sequential
""")
        self.p._load_preference_pickup_strategy()
        self.assertEqual(get_n_next_maps, self.p.map_options_pickup_strategy)

    def test_random(self):
        self.conf.loadFromString("""
[preferences]
map_options_pickup_strategy: random
""")
        self.p._load_preference_pickup_strategy()
        self.assertEqual(get_n_random_maps, self.p.map_options_pickup_strategy)

    def test_junk(self):
        self.conf.loadFromString("""
[preferences]
map_options_pickup_strategy: f00
""")
        self.p._load_preference_pickup_strategy()
        self.assertEqual(get_n_next_maps, self.p.map_options_pickup_strategy)
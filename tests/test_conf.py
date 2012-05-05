# -*- encoding: utf-8 -*-
import StringIO
import logging
import os
from mock import patch, Mock, MagicMock
from mockito import when, unstub, any
from b3.config import CfgConfigParser

from tests import Bf3TestCase
from votemapbf3 import VotemapPlugin
from votemapbf3.map import get_n_next_maps, get_n_random_maps


class ConfTestCase(Bf3TestCase):
    def setUp(self):
        Bf3TestCase.setUp(self)
        self.conf = CfgConfigParser()
        self.p = VotemapPlugin(self.console, self.conf)
        logging.getLogger('output').setLevel(logging.NOTSET)


class Test_default_conf(ConfTestCase):
    def setUp(self):
        ConfTestCase.setUp(self)
        self.conf.load(os.path.join(os.path.dirname(__file__), '../extplugins/conf/plugin_votemapbf3.ini'))
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
        self.assertEqual(0, self.p.nextmap_display_interval)
        self.assertEqual(4, self.p.vote_duration)
        self.assertEqual(0, self.p.vote_threshold)
        self.assertEqual(4, self.p.number_of_vote_options)
        self.assertEqual(True, self.p.exclude_current_map)
        self.assertEqual(True, self.p.exclude_next_map)
        self.assertEqual(get_n_next_maps, self.p.map_options_pickup_strategy)
        self.assertEqual(os.path.normpath(os.path.dirname(__file__) + '/../extplugins/conf/plugin_votemapbf3_maplist.txt'), self.p.map_options_source_file)



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



class Test_maplist_file(ConfTestCase):

    def setUp(self):
        ConfTestCase.setUp(self)

        self.context_manager_mock = MagicMock()
        self.context_manager_mock.__exit__ = Mock()
        self.context_manager_mock.__enter__ = Mock()

        self.open_patcher = patch('__builtin__.open')
        self.open_mock = self.open_patcher.start()
        self.open_mock.return_value = self.context_manager_mock

    def tearDown(self):
        unstub()
        self.open_patcher.stop()

    def test_no_option(self):
        self.conf.loadFromString("""
[preferences]
""")
        self.p._load_preference_map_options_source()
        self.assertIsNone(self.p.map_options_source_file)


    def test_empty_option(self):
        self.conf.loadFromString("""
[preferences]
maplist_file:
""")
        self.p._load_preference_map_options_source()
        self.assertIsNone(self.p.map_options_source_file)


    def test_file_not_found(self):
        self.conf.loadFromString("""
[preferences]
maplist_file: maps.txt
""")
        when(os.path).exists("maps.txt").thenReturn(False)
        self.p._load_preference_map_options_source()
        self.assertIsNone(self.p.map_options_source_file)


    def test_not_a_file(self):
        self.conf.loadFromString("""
[preferences]
maplist_file: maps.txt
""")
        when(os.path).exists("maps.txt").thenReturn(True)
        when(os.path).isfile("maps.txt").thenReturn(False)
        self.p._load_preference_map_options_source()
        self.assertIsNone(self.p.map_options_source_file)


    def test_not_readable(self):
        self.context_manager_mock.__enter__ = Mock(side_effect=IOError('bad'))
        self.conf.loadFromString("""
[preferences]
maplist_file: maps.txt
""")
        when(os.path).exists("maps.txt").thenReturn(True)
        when(os.path).isfile("maps.txt").thenReturn(True)
        self.p._load_preference_map_options_source()
        self.assertIsNone(self.p.map_options_source_file)



    def test_nominal(self):
        self.context_manager_mock.__enter__ = Mock(side_effect=lambda *args, **kwargs: StringIO.StringIO(r"""
MP_007 RushLarge0 2
MP_018 ConquestSmall0 2
MP_Subway RushLarge0 4
MP_003 RushLarge0 4
        """))
        self.conf.loadFromString("""
[preferences]
maplist_file: maps.txt
""")
        when(os.path).exists("maps.txt").thenReturn(True)
        when(os.path).isfile("maps.txt").thenReturn(True)
        self.p._load_preference_map_options_source()
        self.assertEqual('maps.txt', self.p.map_options_source_file)


    def test_filename_full_path_resolution(self):
        self.conf.loadFromString("""
[preferences]
maplist_file: maps.txt
""")
        self.conf.fileName = os.path.normpath('c:/somewhere/conf/plugin_votemapbf3.ini')

        when(os.path).exists(any()).thenReturn(True)
        when(os.path).isfile(any()).thenReturn(True)
        self.p._load_preference_map_options_source()
        self.assertEqual(os.path.normpath('c:/somewhere/conf/maps.txt'), self.p.map_options_source_file)


    def test_full_file_path(self):
        self.conf.loadFromString("""
[preferences]
maplist_file: c:/somewhere/maps.txt
""")
        self.conf.fileName = os.path.normpath('c:/somewhere/conf/plugin_votemapbf3.ini')

        when(os.path).exists(any()).thenReturn(True)
        when(os.path).isfile(any()).thenReturn(True)
        self.p._load_preference_map_options_source()
        self.assertEqual(os.path.normpath('c:/somewhere/maps.txt'), self.p.map_options_source_file)

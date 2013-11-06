# -*- encoding: utf-8 -*-
import StringIO
import logging
from mock import patch, Mock, MagicMock
from b3.config import CfgConfigParser

from tests import Bf3TestCase, Bf4TestCase
from votemapbf3 import VotemapPlugin


class Test_read_maplist_file(Bf3TestCase):
    def setUp(self):
        Bf3TestCase.setUp(self)
        self.conf = CfgConfigParser()
        self.p = VotemapPlugin(self.console, self.conf)
        logger = logging.getLogger('output')
        logger.setLevel(logging.NOTSET)

    @patch("__builtin__.open")
    def test(self, open_mock):
        context_manager_mock = MagicMock()
        open_mock.return_value = context_manager_mock
        context_manager_mock.__exit__ = Mock()
        context_manager_mock.__enter__ = Mock(side_effect=lambda *args, **kwargs: StringIO.StringIO(r"""
MP_007 RushLarge0 2
MP_018 ConquestSmall0 2
# comment
MP_Subway RushLarge0 4
MP_003 RushLarge0 4
    """))
        maplist_block = self.p._read_maplist_file('f00')
        self.assertEqual("MapListBlock[MP_007:RushLarge0:2, MP_018:ConquestSmall0:2, MP_Subway:RushLarge0:4, MP_003:RushLarge0:4]", str(maplist_block))


class Test_make_map_label(Bf3TestCase):
    def setUp(self):
        Bf3TestCase.setUp(self)
        self.conf = CfgConfigParser()
        self.p = VotemapPlugin(self.console, self.conf)
        self.p.onLoadConfig()
        self.p.onStartup()

    def test_nominal(self):
        self.assertEqual("Caspian Border (Rush)", self.p._make_map_label({
            "gamemode": "RushLarge0",
            "name": "MP_007"
        }))

    def test_unknown_gamemode(self):
        self.assertEqual("Caspian Border", self.p._make_map_label({
            "gamemode": "Elimination0",
            "name": "MP_007"
        }))

    def test_unknown_map(self):
        self.assertEqual("f00 (Rush)", self.p._make_map_label({
            "gamemode": "RushLarge0",
            "name": "f00"
        }))


class Test_make_map_label(Bf4TestCase):
    def setUp(self):
        Bf4TestCase.setUp(self)
        self.conf = CfgConfigParser()
        self.p = VotemapPlugin(self.console, self.conf)
        self.p.onLoadConfig()
        self.p.onStartup()

    def test_nominal(self):
        self.assertEqual("Operation Locker (Defuse)", self.p._make_map_label({
            "gamemode": "Elimination0",
            "name": "MP_Prison"
        }))

    def test_unknown_gamemode(self):
        self.assertEqual("Siege of Shanghai", self.p._make_map_label({
            "gamemode": "f00",
            "name": "MP_Siege"
        }))

    def test_unknown_map(self):
        self.assertEqual("f00 (Rush)", self.p._make_map_label({
            "gamemode": "RushLarge0",
            "name": "f00"
        }))
# -*- encoding: utf-8 -*-
import StringIO
import logging
from mock import patch, Mock, MagicMock
from b3.config import CfgConfigParser

from tests import Bf3TestCase
from votemapbf3 import VotemapPlugin


class TestCase(Bf3TestCase):
    def setUp(self):
        Bf3TestCase.setUp(self)
        self.conf = CfgConfigParser()
        self.p = VotemapPlugin(self.console, self.conf)
        logger = logging.getLogger('output')
        logger.setLevel(logging.NOTSET)


class Test_read_maplist_file(TestCase):

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
import os
import sys
from mock import Mock
from b3.clients import Client
from b3.config import CfgConfigParser
from b3.plugins.admin import AdminPlugin
from votemapbf3 import VotemapPlugin
from votemapbf3.vote import VoteSession

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest


mapinfo_grand_bazaar = {'name': 'MP_001', 'gamemode': 'gamemode', 'num_of_rounds': '2', 'label': 'Grand Bazaar'}
mapinfo_teheran_highway = {'name': 'MP_003', 'gamemode': 'gamemode', 'num_of_rounds': '2', 'label': 'Teheran Highway' }
    
class VoteSession_TestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = CfgConfigParser()
        cls.config.read(os.path.join(os.path.dirname(__file__), '../extplugins/conf/plugin_votemapbf3.ini'))

    def setUp(self):
        self.plugin = Mock(VotemapPlugin)
        self.vs = VoteSession(self.plugin, Mock(spec=AdminPlugin), dict(self.__class__.config.items('messages', raw=True)))


class Test_start(VoteSession_TestCase):
    def test_zero_option_cannot_start(self):
        self.assertRaises(AssertionError, self.vs.start)

    def test_one_option_cannot_start(self):
        self.vs.addOption(mapinfo_grand_bazaar)
        self.assertRaises(AssertionError, self.vs.start)

    def test_two_options_can_start(self):
        self.vs.addOption(mapinfo_grand_bazaar)
        self.vs.addOption(mapinfo_teheran_highway)
        self.vs.start()
        self.assertIsNotNone(self.vs.start_time)

    def test_not_started_ignore_votes(self):
        self.vs.addOption(mapinfo_grand_bazaar)
        self.vs.addOption(mapinfo_teheran_highway)
        self.assertEqual(0, len(self.vs.votes))
        player1 = Mock(spec=Client)
        player1.cid = 'player1'
        self.vs.vote(player1, 'MP_001')
        self.assertEqual(0, len(self.vs.votes))
        self.vs.start()
        self.vs.vote(player1, '1')
        self.assertEqual(1, len(self.vs.votes))


class Test_getOptions(VoteSession_TestCase):
    def test_empty(self):
        self.assertListEqual([], self.vs.getOptions())

    def test_one_option(self):
        self.vs.addOption(mapinfo_grand_bazaar)
        self.assertListEqual([('1', 'Grand Bazaar')], self.vs.getOptions())

    def test_multiple_options(self):
        self.vs.addOption(mapinfo_grand_bazaar)
        self.vs.addOption(mapinfo_teheran_highway)
        self.assertListEqual([('1', 'Grand Bazaar'), ('2', 'Teheran Highway')], self.vs.getOptions())


class Test_getCounts(VoteSession_TestCase):
    def test_no_vote(self):
        self.assertDictEqual({}, dict(self.vs.getCounts()))
        self.vs.addOption(mapinfo_grand_bazaar)
        self.assertDictEqual({}, dict(self.vs.getCounts()))
        self.vs.addOption(mapinfo_teheran_highway)
        self.assertDictEqual({}, dict(self.vs.getCounts()))

    def test_votes(self):
        self.vs.addOption(mapinfo_grand_bazaar)
        self.vs.addOption(mapinfo_teheran_highway)
        self.vs.start()
        self.vs.vote(Mock(), '1')
        self.assertDictEqual({'1': 1}, dict(self.vs.getCounts()))
        self.vs.vote(Mock(), '1')
        self.assertDictEqual({'1': 2}, dict(self.vs.getCounts()))
        self.vs.vote(Mock(), '2')
        self.assertDictEqual({'1': 2, '2': 1}, dict(self.vs.getCounts()))


class Test_getCurrentVotesAsTextLines(VoteSession_TestCase):
    def test_no_vote(self):
        self.assertEqual("", self.vs.getCurrentVotesAsTextLines())

    def test_votes(self):
        self.vs.addOption(mapinfo_grand_bazaar)
        self.vs.addOption(mapinfo_teheran_highway)
        self.vs.start()
        self.assertEqual('Grand Bazaar: 0, Teheran Highway: 0', self.vs.getCurrentVotesAsTextLines())
        self.vs.vote(Mock(), '1')
        self.assertEqual('Grand Bazaar: 1, Teheran Highway: 0', self.vs.getCurrentVotesAsTextLines())
        self.vs.vote(Mock(), '1')
        self.assertEqual('Grand Bazaar: 2, Teheran Highway: 0', self.vs.getCurrentVotesAsTextLines())
        self.vs.vote(Mock(), '2')
        self.assertEqual('Grand Bazaar: 2, Teheran Highway: 1', self.vs.getCurrentVotesAsTextLines())



class Test_getWinningOption(VoteSession_TestCase):
    def test_no_option(self):
        self.assertIsNone(self.vs.getWinningOption())

    def test_one_option_no_vote(self):
        self.vs.addOption(mapinfo_grand_bazaar)
        self.assertIsNone(self.vs.getWinningOption())

    def test_two_options_no_vote(self):
        self.vs.addOption(mapinfo_grand_bazaar)
        self.vs.addOption(mapinfo_teheran_highway)
        self.assertIsNone(self.vs.getWinningOption())

    def test_votes(self):
        self.vs.addOption(mapinfo_grand_bazaar)
        self.vs.addOption(mapinfo_teheran_highway)
        self.vs.start()
        self.assertIsNone(self.vs.getWinningOption())
        self.vs.vote(Mock(), '1')
        self.assertIsNone(self.vs.getWinningOption(min_votes=2))
        self.assertDictEqual(mapinfo_grand_bazaar, self.vs.getWinningOption(min_votes=1))
        self.assertDictEqual(mapinfo_grand_bazaar, self.vs.getWinningOption())
        self.vs.vote(Mock(), '1')
        self.assertIsNone(self.vs.getWinningOption(min_votes=3))
        self.assertDictEqual(mapinfo_grand_bazaar, self.vs.getWinningOption(min_votes=2))
        self.assertDictEqual(mapinfo_grand_bazaar, self.vs.getWinningOption())
        self.vs.vote(Mock(), '2')
        self.vs.vote(Mock(), '2')
        self.assertIsNone(self.vs.getWinningOption())
        self.vs.vote(Mock(), '2')
        self.assertDictEqual(mapinfo_teheran_highway, self.vs.getWinningOption())



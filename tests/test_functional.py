from mock import Mock, call, patch
import time
from parsers.frostbite2.util import MapListBlock
from tests import Bf3TestCase
from b3.config import CfgConfigParser
from votemapbf3 import VotemapPlugin

class Test_command_cancelvote(Bf3TestCase):
    def setUp(self):
        Bf3TestCase.setUp(self)
        self.conf = CfgConfigParser()
        self.conf.loadFromString("""\
[commands]
cancelvote-cv: 20
""")
        self.p = VotemapPlugin(self.console, self.conf)
        self.p.onLoadConfig()
        self.p.onStartup()

    def test_no_vote(self):
        self.admin.connects('admin')
        self.admin.says('!cancelvote')
        self.assertEqual(['There is no vote to cancel'], self.admin.message_history)

    def test_nominal(self):
        self.admin.connects('admin')
        self.p.current_vote_session = Mock()
        self.p.current_vote_session_timer = Mock()
        self.admin.says('!cancelvote')
        self.assertEqual(['Vote canceled'], self.admin.message_history)
        self.assertIsNone(self.p.current_vote_session)
        self.assertIsNone(self.p.current_vote_session_timer)

    def test_alias(self):
        self.admin.connects('admin')
        self.admin.clearMessageHistory()
        self.admin.says('!cv')
        self.assertEqual(['There is no vote to cancel'], self.admin.message_history)


class Votesession_TestCase(Bf3TestCase):
    map_list = MapListBlock(
        ['3', '3', 'MP_001', 'RushLarge0', '1', 'MP_003', 'ConquestSmall0', '2', 'MP_007', 'SquadDeathMatch0', '3'])

    @staticmethod
    def write(data):
        """ simulate the write method of the B3 parser used to communicate with the BF3 server """
        if data == ('mapList.getMapIndices',):
            return ['0', '1']

    def setUp(self):
        Bf3TestCase.setUp(self)
        self.conf = CfgConfigParser()
        self.conf.loadFromString(self.__class__.CONFIG)
        self.p = VotemapPlugin(self.console, self.conf)
        self.p.onLoadConfig()
        self.p.onStartup()

        self.getFullMapRotationList_patcher = patch.object(self.console, 'getFullMapRotationList',
            Mock(return_value=Test_command_votemap.map_list))
        self.getFullMapRotationList_patcher.start()

        self.write_patcher = patch.object(self.console, 'write', wraps=Test_command_votemap.write)
        self.write_mock = self.write_patcher.start()

    def tearDown(self):
        Bf3TestCase.tearDown(self)
        if hasattr(self.p, 'current_vote_session_timer') and self.p.current_vote_session_timer:
            self.p.current_vote_session_timer.cancel()
        self.getFullMapRotationList_patcher.stop()
        self.write_patcher.stop()


class Test_command_votemap(Votesession_TestCase):
    CONFIG = """\
[commands]
votemap: 0
"""

    def test_nominal(self):
        # GIVEN
        self.console.say = Mock()
        self.joe.connects("joe")

        # WHEN
        self.joe.says('!votemap')

        # THEN
        self.assertEqual(['New vote session started'], self.joe.message_history)
        self.assertIsNotNone(self.p.current_vote_session)
        self.assertIsNotNone(self.p.current_vote_session_timer)
        self.console.say.assert_called_once_with('Type: /1, /2, ... in chat to vote for the next map')
        self.console.write.assert_has_calls([])


    def test_vote_cast(self):
        # GIVEN
        self.test_nominal()

        # WHEN
        self.joe.clearMessageHistory()
        self.joe.connects("joe")
        self.joe.says('/1')

        # THEN
        self.assertEqual(['You voted for map Tehran Highway'], self.joe.message_history)


    def test_already_started(self):
        # GIVEN
        self.test_nominal()

        # WHEN
        self.simon.connects("simon")
        self.simon.says("!votemap")

        # THEN
        self.assertEqual(['A vote is already in progress'], self.simon.message_history)


    def test_2nd_votemap_call_after_first_failing_to_change_map(self):
        # GIVEN
        # a normal vote that ends without having received any vote
        self.test_nominal()
        self.p.stop_current_vote_session()
        self.assertIsNone(self.p.last_vote_start_time)

        # WHEN
        self.simon.connects("simon")
        self.simon.says("!votemap")

        # THEN
        self.assertEqual(['New vote session started'], self.simon.message_history)


    def test_last_vote_too_recent(self):
        # GIVEN
        # a normal vote that ends with success
        self.test_nominal()
        self.joe.says('/1') # vote for a map
        self.p.stop_current_vote_session()
        self.assertIsNotNone(self.p.last_vote_start_time)

        # WHEN
        self.simon.connects("simon")
        self.simon.says("!votemap")

        # THEN
        self.assertEqual(['Next map vote allowed in 5 minutes'], self.simon.message_history)


    def test_vote_ended_by_timer(self):
        # GIVEN
        self.p.vote_duration = .1 / 60 # seconds in munute
        self.test_nominal()
        self.joe.says('/1') # vote for a map
        self.console.say.reset_mock()
        saybig_mock = self.console.saybig = Mock()

        # WHEN
        self.console.say.assert_has_calls([])
        time.sleep(.2)

        # THEN
        self.console.say.assert_called_once_with('Voted map : Tehran Highway')
        saybig_mock.assert_called_once_with('Voted map : Tehran Highway')
        self.write_mock.assert_has_calls([call(('mapList.setNextMapIndex', 1))])


class Test_command_v(Votesession_TestCase):
    CONFIG = """\
[commands]
votemap: 0
v: 0
"""

    def test_no_vote_in_progress(self):
        # GIVEN
        self.console.say = Mock()
        self.joe.connects("joe")

        # WHEN
        self.joe.says('!v')

        # THEN
        self.assertEqual(['no vote in progress, type !votemap to request a vote'], self.joe.message_history)


    def test_nominal(self):
        # GIVEN
        self.simon.connects("simon")
        self.simon.says('!votemap')
        self.assertEqual(['New vote session started'], self.simon.message_history)
        self.assertIsNotNone(self.p.current_vote_session)
        self.assertIsNotNone(self.p.current_vote_session_timer)

        # WHEN
        self.joe.connects("joe")
        self.write_mock.reset_mock()
        self.joe.says('!v')

        # THEN
        self.write_mock.assert_has_calls(
            [call(('admin.say', ' /1 Tehran Highway            | /2 Caspian Border           ', 'player', 'joe')),
             call(('admin.say', ' /3 Grand Bazaar              ', 'player', 'joe'))])
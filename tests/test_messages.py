# -*- encoding: utf-8 -*-
import logging
import os
from mock import Mock
from b3.config import CfgConfigParser

from tests import Bf3TestCase
from votemapbf3 import VotemapPlugin
from votemapbf3.map import get_n_next_maps, get_n_random_maps


messages_keys = (
    'vote_announcement_started',
    'vote_announcement_cancel',
    'votemap_feedback_interval_error',
    'votemap_feedback_in_progress_error',
    'votemap_feedback_not_enough_maps',
    'votemap_feedback_success',
    'cancelvote_feedback_success',
    'cancelvote_feedback_no_vote_in_progress',
    'votecast_feedback_success',
    'voteresult_no_map_chosen',
    'voteresult_map_chosen',
    'v_feedback_no_vote_in_progress',
    )

class ConfTestCase(Bf3TestCase):
    def setUp(self):
        Bf3TestCase.setUp(self)
        self.conf = CfgConfigParser()
        self.p = VotemapPlugin(self.console, self.conf)
        logger = logging.getLogger('output')
        logger.setLevel(logging.INFO)


    def test_default_messages(self):
        # GIVEN
        self.conf.loadFromString(r"""
[messages]
        """)
        # WHEN
        self.p._load_messages()
        # THEN
        for msg_key in messages_keys:
            self.assertIn(msg_key, self.p._messages)
            self.assertTrue(self.p._messages[msg_key])


    def test_default_config(self):
        # GIVEN
        self.conf.load(os.path.join(os.path.dirname(__file__), '../extplugins/conf/plugin_votemapbf3.ini'))
        self.p._messages = {}
        # WHEN
        self.p._load_messages()
        # THEN
        for msg_key in messages_keys:
            self.assertIn(msg_key, self.p._messages)
            self.assertTrue(self.p._messages[msg_key])


    def test_custom_messages(self):
        # GIVEN
        self.conf.loadFromString(r"""
[messages]
msg2: custom messages for msg2
        """)
        # WHEN
        self.p._messages = {
            'msg1': 'this is the default message for msg1',
            'msg2': 'this is the default message for msg2'
        }
        self.p._load_messages()
        # THEN
        self.assertEqual("this is the default message for msg1", self.p._messages['msg1'])
        self.assertEqual("this is the default message for msg1", self.p.getMessage('msg1'))
        self.assertEqual("custom messages for msg2", self.p._messages['msg2'])
        self.assertEqual("custom messages for msg2", self.p.getMessage('msg2'))


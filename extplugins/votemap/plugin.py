# -*- coding: utf-8 -*-
#
# Votemap BF3 Plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2012 courgette@bigbrotherbot.net
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#
import ConfigParser
from threading import Timer
import time
import b3
from b3.functions import minutesStr
from b3.plugin import Plugin
from vote import VoteSession
from votemap.map import get_n_next_maps, get_n_random_maps
from votemap.util import two_by_two
from votemap.bf3string import ljust


class VotemapPlugin(Plugin):
    def __init__(self, console, config=None):
        self._adminPlugin = None

        # default messages
        self._messages = {
            "vote_announcement_started": "Type: /1, /2, ... in chat to vote for the next map",
            "vote_announcement_cancel": "Vote canceled",
            "votemap_feedback_interval_error": "Next map vote allowed in %(time)s",
            "votemap_feedback_in_progress_error": "A vote is already in progress",
            "votemap_feedback_success": "New vote session started",
            "cancelvote_feedback_success": "Vote canceled",
            "cancelvote_feedback_no_vote_in_progress": "There is no vote to cancel",
            "votecast_feedback_success": "You voted for map %(map)s",
            "voteresult_no_map_chosen": "No single map won the vote",
            "voteresult_map_chosen": "Voted map : %(map)s",
            "v_feedback_no_vote_in_progress": "no vote in progress, type !votemap to request a vote",
            }

        self.vote_interval = None
        self.nextmap_display_interval = None
        self.vote_duration = None
        self.vote_threshold = None
        self.number_of_vote_options = None
        self.exclude_current_map = None
        self.exclude_next_map = None
        self.map_options_pickup_strategy = None

        self.current_vote_session = None
        self.last_vote_start_time = None

        Plugin.__init__(self, console, config)


    ################################################################################################################
    #
    #    Plugin interface implementation
    #
    ################################################################################################################

    def onLoadConfig(self):
        """\
        This is called after loadConfig(). Any plugin private variables loaded
        from the config need to be reset here.
        """
        self._load_messages()
        self._load_preferences()
        self._load_preference_pickup_strategy()


    def onStartup(self):
        """\
        Initialize plugin settings
        """
        # get the admin plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # something is wrong, can't start without admin plugin
            self.error('Could not find admin plugin')
            return False
        self._registerCommands()

        # Register our events
        self.registerEvent(b3.events.EVT_GAME_MAP_CHANGE)
        self.registerEvent(b3.events.EVT_CLIENT_DISCONNECT)


    def onEvent(self, event):
        """\
        Handle intercepted events
        """
        if event.type == b3.events.EVT_GAME_MAP_CHANGE:
            self.cancel_current_vote_session()

        elif event.type == b3.events.EVT_CLIENT_DISCONNECT:
            if self.current_vote_session:
                self.current_vote_session.removeVoter(event.client)


    def disable(self):
        self.cancel_current_vote_session()
        Plugin.disable(self)


    ################################################################################################################
    #
    #   Commands implementations
    #
    ################################################################################################################

    def cmd_votemap(self, data, client, cmd=None):
        """\
        Start a vote for the next map
        """
        if self.current_vote_session:
            client.message(self.getMessage('votemap_feedback_in_progress_error'))
        else:
            self.start_vote_session(client)

    def cmd_cancelvote(self, data, client, cmd=None):
        """\
        Cancel the current vote
        """
        if not self.current_vote_session:
            client.message(self.getMessage('cancelvote_feedback_no_vote_in_progress'))
        else:
            self.cancel_current_vote_session()
            client.message(self.getMessage('cancelvote_feedback_success'))

    def _cmd_vote(self, data, client, cmd=None):
        """\
        vote for a map
        """
        if self.current_vote_session:
            self.current_vote_session.vote(client, cmd.command)

    def cmd_v(self, data, client, cmd=None):
        """\
        Display current vote options
        """
        if not self.current_vote_session:
            client.message(self.getMessage("v_feedback_no_vote_in_progress"))
        else:
            self.announce_vote_options(client)


    ################################################################################################################
    #
    #   Other methods
    #
    ################################################################################################################

    def announce_vote_options(self, client=None):
        """display the vote options to all players or the given player"""

        def write(txt, client=None):
            if txt[0] == '/': # if line starts with '/', then it won't be displayed by the BF3 server
                txt = ' ' + txt
            if client:
                self.console.write(("admin.say", txt, 'player', client.cid ))
            else:
                self.console.write(("admin.say", txt, 'all'))

        for two_options in two_by_two(self.current_vote_session.getOptions()):
            options = [ljust("/%s %s" % x, pct=48) for x in two_options]
            write(" | ".join(options), client)

    def start_vote_session(self, client=None):
        if self.last_vote_start_time:
            now = time.time()
            how_long_ago = now - self.last_vote_start_time
            next_vote_allowed_seconds = self.last_vote_start_time + (self.vote_interval * 60) - now
            if how_long_ago < self.vote_interval * 60:
                self.info(
                    "cannot start vote because a previous vote started less than %s" % minutesStr(self.vote_interval))
                if client:
                    client.message(self.getMessage('votemap_feedback_interval_error',
                            {'time': minutesStr("%ss" % next_vote_allowed_seconds)}))
                return

        # get the maps to choose from
        available_maps = self.console.getFullMapRotationList()
        map_indices = self.console.write(('mapList.getMapIndices',))
        excluded_indices = []
        if self.exclude_current_map:
            excluded_indices.append(map_indices[0])
        if self.exclude_next_map:
            excluded_indices.append(map_indices[1])
        options = get_n_next_maps(available_maps, self.number_of_vote_options, map_indices[0], excluded_indices)

        self.current_vote_session = VoteSession(self, self._adminPlugin, self._messages)
        for i in options:
            self.current_vote_session.addOption(i, self.console.getEasyName(available_maps[i]['name']))
        self.current_vote_session.start()

        self.console.say(self.getMessage("vote_announcement_started"))
        time.sleep(.5)
        self.announce_vote_options()
        self.current_vote_session_timer = Timer(interval=self.vote_duration * 60,
            function=self.stop_current_vote_session)
        self.current_vote_session_timer.start()

        if client:
            client.message(self.getMessage('votemap_feedback_success'))


    def stop_current_vote_session(self):
        """End the current vote session"""
        if self.current_vote_session:
            self.current_vote_session.stop()

            winning_option = self.current_vote_session.getWinningOption(min_votes=self.vote_threshold)
            if winning_option:
                self.last_vote_start_time = self.current_vote_session.getStartTime()
                self.console.write(('mapList.setNextMapIndex', winning_option['map_id']))
                self.console.say(self.getMessage("voteresult_map_chosen", {'map': winning_option['label']}))
                self.console.saybig(self.getMessage("voteresult_map_chosen", {'map': winning_option['label']}))
                self.current_vote_session = None
            else:
                self.console.say(self.getMessage("voteresult_no_map_chosen"))

            self.__reset_current_vote_session()


    def cancel_current_vote_session(self):
        if self.current_vote_session:
            self.__reset_current_vote_session()
            self.console.say(self.getMessage('vote_announcement_cancel'))

    def __reset_current_vote_session(self):
        self.current_vote_session = None
        if self.current_vote_session_timer:
            self.current_vote_session_timer.cancel()
            self.current_vote_session_timer = None

    def _registerCommands(self):
        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp
                func = getattr(self, "cmd_" + cmd, None)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)
                else:
                    self.warning("config defines unknown command '%s'" % cmd)

    def _load_messages(self):
        """ loads messages from config """
        if self.config.has_section('messages'):
            self._messages.update(dict(self.config.items('messages', raw=True)))

    def _load_preferences(self):
        self.vote_interval = self._load_preference(self.config.getint, 'vote_interval', 5)
        self.nextmap_display_interval = self._load_preference(self.config.getint, 'nextmap_display_interval', 120)
        self.vote_duration = self._load_preference(self.config.getint, 'vote_duration', 4)
        self.vote_threshold = self._load_preference(self.config.getint, 'vote_threshold', 0)
        self.number_of_vote_options = self._load_preference(self.config.getint, 'number_of_vote_options', 4)
        self.exclude_current_map = self._load_preference(self.config.getboolean, 'exclude_current_map', True)
        self.exclude_next_map = self._load_preference(self.config.getboolean, 'exclude_next_map', True)

    def _load_preference_pickup_strategy(self):
        default_value = 'sequential'
        try:
            value = self.config.get('preferences', "map_options_pickup_strategy")
            if value not in ('sequential', 'random'):
                raise ValueError('expecting one of sequential/random')
        except ConfigParser.NoOptionError, err:
            self.warning("Cannot find config option preferences.map_options_pickup_strategy. Using default value instead")
            value = default_value
        except ValueError, err:
            self.warning("Cannot read value for config option preferences.map_options_pickup_strategy. Expecting one of sequential/random. Using default value instead")
            value = default_value
        self.info("config option preferences.map_options_pickup_strategy : %s" % value)

        if value == 'sequential':
            self.map_options_pickup_strategy = get_n_next_maps
        elif value == 'random':
            self.map_options_pickup_strategy = get_n_random_maps
        else:
            raise ValueError("unexpected value '%s' for the map pickup strategy" % value)


    def _load_preference(self, getter_func, name, default_value=None):
        try:
            value = getter_func('preferences', name)
        except ConfigParser.NoOptionError, err:
            self.warning("Cannot find config option preferences.%s. Using default value instead" % name)
            value = default_value
        except ValueError, err:
            self.warning("Cannot read value for config option preferences.%s. %s. Using default value instead" % (
                name, err.message))
            value = default_value
        self.info("config option preferences.%s : %s" % (name, value))
        return value

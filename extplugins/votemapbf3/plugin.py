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
import os
import re
from threading import Timer
import threading
import time
import b3
from b3.functions import minutesStr
from b3.plugin import Plugin
from b3.parsers.frostbite2.util import MapListBlock
from vote import VoteSession
from votemapbf3.map import get_n_next_maps, get_n_random_maps
from votemapbf3.util import two_by_two
from votemapbf3.bf3string import ljust

from votemapbf3 import __version__ as plugin_version
__version__ = plugin_version # we need this trick to have the publist plugin report the correct version to B3 master


GAME_MODES_SHORTNAMES = {
    "ConquestLarge0": "ConqL",
    "ConquestSmall0": "Conq",
    "ConquestSmall1": "ConqA", # will be deprecated after BF3 server R20
    "ConquestAssaultLarge0": "ConqAL",
    "ConquestAssaultSmall0": "ConqA",
    "ConquestAssaultSmall1": "ConqA2",
    "RushLarge0": "Rush",
    "SquadRush0": "SQRH",
    "SquadDeathMatch0": "SQDM",
    "TeamDeathMatch0": "TDM",
    }

class VotemapPlugin(Plugin):
    def __init__(self, console, config=None):
        self._adminPlugin = None

        self.vote_interval = None
        self.nextmap_display_interval = None
        self.vote_duration = None
        self.vote_threshold = None
        self.number_of_vote_options = None
        self.exclude_current_map = None
        self.exclude_next_map = None
        self.map_options_pickup_strategy = None
        self.map_options_source_file = None

        self.current_vote_session = None
        self.current_vote_session_timer = None
        self.last_vote_start_time = None

        self.nextmap_timer = None

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
        self._load_default_messages()
        self._load_messages()
        self._load_preferences()
        self._load_preference_pickup_strategy()
        self._load_preference_map_options_source()
        self._init_nextmap_display_timer()


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


    def enable(self):
        Plugin.enable(self)
        self._init_nextmap_display_timer()

    def disable(self):
        self.cancel_current_vote_session()
        self._cancel_nextmap_display_timer()
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
        available_maps = self._getAvailableMaps()
        self.debug("available maps : %s" % available_maps)
        current_mapinfo = self._get_current_mapinfo()

        excluded_maps = []
        if self.exclude_current_map:
            excluded_maps.append(current_mapinfo)
        if self.exclude_next_map:
            excluded_maps.append(self._get_next_mapinfo())

        options = self.map_options_pickup_strategy(available_maps, self.number_of_vote_options, current_mapinfo, excluded_maps)

        if len(options) >= 2:
            self.current_vote_session = VoteSession(self, self._adminPlugin, self._messages)
            for mapinfo in options:
                mapinfo['label'] = self._make_map_label(mapinfo)
                self.current_vote_session.addOption(mapinfo)
            self.current_vote_session.start()

            self.console.say(self.getMessage("vote_announcement_started"))
            time.sleep(.5)
            self.announce_vote_options()
            self.current_vote_session_timer = Timer(interval=self.vote_duration * 60,
                function=self.stop_current_vote_session)
            self.current_vote_session_timer.start()

            if client:
                client.message(self.getMessage('votemap_feedback_success'))
        else:
            self.warning("cannot start a vote with less than 2 options")
            if client:
                client.message(self.getMessage('votemap_feedback_not_enough_maps'))


    def stop_current_vote_session(self):
        """End the current vote session"""
        if self.current_vote_session:
            self.current_vote_session.stop()

            winning_option = self.current_vote_session.getWinningOption(min_votes=self.vote_threshold)
            if winning_option:
                self.last_vote_start_time = self.current_vote_session.getStartTime()
                self._set_next_map(winning_option['name'],  winning_option['gamemode'], winning_option['num_of_rounds'])
                self.console.say(self.current_vote_session.getCurrentVotesAsTextLines())
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


    def _load_default_messages(self):
        self._messages = {
            "vote_announcement_started": "Type: /1, /2, ... in chat to vote for the next map",
            "vote_announcement_cancel": "Vote canceled",
            "votemap_feedback_interval_error": "Next map vote allowed in %(time)s",
            "votemap_feedback_in_progress_error": "A vote is already in progress",
            "votemap_feedback_not_enough_maps": "Not enough maps to vote for",
            "votemap_feedback_success": "New vote session started",
            "cancelvote_feedback_success": "Vote canceled",
            "cancelvote_feedback_no_vote_in_progress": "There is no vote to cancel",
            "votecast_feedback_success": "You voted for map %(map)s",
            "voteresult_no_map_chosen": "No single map won the vote",
            "voteresult_map_chosen": "Voted map : %(map)s",
            "v_feedback_no_vote_in_progress": "no vote in progress, type !votemap to request a vote",
            }


    def _load_preferences(self):
        self.vote_interval = self._load_preference(self.config.getint, 'vote_interval', 5)
        self.nextmap_display_interval = self._load_preference(self.config.getint, 'nextmap_display_interval', 0)
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


    def _load_preference_map_options_source(self):
        default_value = None
        try:
            file_path = self.config.getpath('preferences', "maplist_file")
            if file_path:
                basename = os.path.basename(file_path)
                if basename == file_path and self.config.fileName:
                    # no path specified, assume same path as plugin config file
                    file_path = os.path.normpath(os.path.dirname(self.config.fileName) + '/' + basename)
                if not os.path.exists(file_path):
                    raise ValueError('"%s" cannot be found' % file_path)
                elif not os.path.isfile(file_path):
                    raise ValueError('"%s" is not a file' % file_path)
                else:
                    with open(file_path, mode='r') as f:
                        f.read()
        except ConfigParser.NoOptionError, err:
            self.info("Cannot find config option preferences.maplist_file. Using server map rotation list instead")
            file_path = default_value
        except ValueError, err:
            self.warning("invalid value for config option preferences.maplist_file. Using server map rotation list instead. %s" % err)
            file_path = default_value
        except Exception, err:
            self.warning("error while reading config option preferences.maplist_file. Using server map rotation list instead. %r" % err)
            file_path = default_value

        if file_path:
            self.info("maps will be picked up from %s" % file_path)
            self.map_options_source_file = file_path
        else:
            self.info("maps will be picked up from the server rotation list")
            self.map_options_source_file = None


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


    def _read_maplist_file(self, filename):
        """ open a file respecting the maplist file format as described in the official BF3 Server Administration
        guide and return a MapListBlock object representing its content.
        Able to exclude badly formatted lines.
        """
        re_valid_map_line = re.compile(r"^\s*(?P<map_info>[^#]\w+\s+\w+\s+\d+)\s*(?:#.*)?$")
        valid_lines = []
        with open(filename, mode='r') as f:
            for raw_line in f:
                match = re_valid_map_line.match(raw_line)
                if match:
                    valid_lines.append(match.group('map_info'))
        self.debug("valid lines : \n%s" % '\n'.join(valid_lines))
        maps = MapListBlock([len(valid_lines), 3] + re.sub('\s+', ' ', '   '.join(valid_lines)).split(' '))
        return maps


    def _getAvailableMaps(self):
        """ return a MapListBlock object with all maps elegible as a vote option.
        will take those maps either from the current server map rotation list or a file
        depending on the plugin config.
        """
        if self.map_options_source_file:
            try:
                maps = self._read_maplist_file(self.map_options_source_file)
                self.debug("maps from %s : %s" % (self.map_options_source_file, maps))
            except Exception, err:
                self.error("Failed to read maps from %s. %s" % (self.map_options_source_file, err))
                maps =  self.console.getFullMapRotationList()
                self.debug("maps from current rotation list : %s" % maps)
        else:
            maps = self.console.getFullMapRotationList()
            self.debug("maps from current rotation list : %s" % maps)
        return maps


    def _get_current_mapinfo(self):
        self.console.getServerInfo()
        return {'name': self.console.game.mapName, 'gamemode': self.console.game.gameType, 'num_of_rounds': self.console.game.serverinfo["roundsTotal"]}


    def _get_next_mapinfo(self):
        maps = self.console.getFullMapRotationList()
        if not len(maps):
            return self._get_current_mapinfo()
        else:
            map_indices = self.console.write(('mapList.getMapIndices',))
            nextmap_indice = int(map_indices[1])
            try:
                return maps[nextmap_indice]
            except IndexError:
                return maps[0]


    def _set_next_map(self, map_id, gamemode, num_of_rounds):
        map_info = {'name': map_id, 'gamemode': gamemode, 'num_of_rounds': num_of_rounds}
        maps = list(self.console.getFullMapRotationList())
        if map_info in maps:
            # next map is already in server rotation list
            map_indices = self.console.write(('mapList.getMapIndices',))
            currentmap_indice = int(map_indices[0])
            try:
                indice_of_next_map = maps.index(map_info,currentmap_indice + 1)
            except ValueError:
                indice_of_next_map = maps.index(map_info, 0, currentmap_indice + 1)
            self.console.write(('mapList.setNextMapIndex', indice_of_next_map))
        else:
            # add next map to server rotation list
            self.console.write(('mapList.add', map_id, gamemode, num_of_rounds))
            self.console.write(('mapList.setNextMapIndex', len(maps)))


    def _make_map_label(self, mapinfo):
        try:
            gamemode_shortlabel = GAME_MODES_SHORTNAMES[mapinfo["gamemode"]]
        except KeyError, err:
            self.error(err)
            gamemode_shortlabel = None
        label = self.console.getEasyName(mapinfo['name'])
        if gamemode_shortlabel:
            label += " (" + gamemode_shortlabel + ")"
        return label


    def _display_nextmap(self):
        self.console.say("nextmap: " + self.console.getNextMap())
        if self.working:
            self._init_nextmap_display_timer()

    def _cancel_nextmap_display_timer(self):
        if self.nextmap_timer:
            self.nextmap_timer.cancel()

    def _init_nextmap_display_timer(self):
        self._cancel_nextmap_display_timer()
        if self.nextmap_display_interval and self.nextmap_display_interval > 0:
            self.nextmap_timer = threading.Timer(interval=self.nextmap_display_interval, function=self._display_nextmap)
            self.nextmap_timer.start()



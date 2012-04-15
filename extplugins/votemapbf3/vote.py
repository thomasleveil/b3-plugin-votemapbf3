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
import sys, time

if sys.version_info[:2] < (2, 7):
    from votemapbf3.util import Counter
else:
    from collections import Counter



class VoteSession(object):
    """Manage a vote by defining the available options and counting the votes"""

    def __init__(self, plugin, adminPlugin, messages):
        self.plugin = plugin
        self.adminPlugin = adminPlugin
        self.options = {}
        self.votes = {}
        self.start_time = None
        self.ended = None
        self.messages = messages

    def addOption(self, map_id, label):
        assert not self.start_time, "Cannot add option after vote session started"
        self.options[str(len(self.options) + 1)] = {'map_id': map_id, 'label': label}

    def start(self):
        """starts the vote session and accepts vote casts"""
        assert len(self.options) >= 2, "Cannot start a vote with less than 2 options"
        for option_id in self.options.keys():
            self.adminPlugin.registerCommand(self.plugin, option_id, 0, self.plugin._cmd_vote)
        self.start_time = time.time()
        self.ended = False

    def stop(self):
        """stops the vote session and refuses any new vote cast"""
        for option_id in self.options.keys():
            del self.adminPlugin._commands[option_id]
        self.ended = True

    def vote(self, player, option_key):
        if self.start_time:
            if self.ended:
                self.plugin.debug("%s trying to vote on a ended vote session" % player.cid)
            else:
                try:
                    option = self.options[option_key]
                except KeyError:
                    return
                else:
                    self.votes[player.cid] = option_key
                    player.message(self.messages['votecast_feedback_success'] % {'map': option['label']})

    def removeVoter(self, player):
        if player.cid in self.votes:
            del self.votes[player.cid]

    def getCounts(self):
        """return a Counter object having option_key as keys"""
        counts = Counter()
        for voter, option_key in self.votes.iteritems():
            counts[option_key] += 1
        return counts

    def getStartTime(self):
        return self.start_time

    def getCurrentVotesAsTextLines(self):
        """return a list of lines of text representing the current counts for each option as a bar"""
        lines = []
        counts = self.getCounts()
        for option_key in sorted(self.options):
            lines.append(option_key + ": " + ("*" * counts[option_key]))
        return lines

    def getOptions(self):
        """return a list of (option_key, option_label)"""
        options = []
        for option_key in sorted(self.options):
            options.append((option_key, self.options[option_key]['label']))
        return options

    def getWinningOption(self, min_votes=0):
        """return the option info having the most votes and having at least min_votes"""
        counts = self.getCounts()
        winning_options = [k for k, count in counts.iteritems() if
                           count == max(counts.itervalues()) and count >= min_votes]
        if len(winning_options) == 1:
            option_key = winning_options[0]
            return self.options[option_key]
        return None

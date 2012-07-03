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
__version__ = '1.2.2'
__author__ = 'Courgette'

from b3 import __version__ as b3_version
from b3.update import B3version

B3_VERSION_REQUIRED = '1.8.2dev2'
assert B3version(b3_version) >= B3version(
    B3_VERSION_REQUIRED), "The votemap plugin requires B3 %s or later. You current version is %s" % (B3_VERSION_REQUIRED, b3_version)

from plugin import VotemapPlugin

Votemapbf3Plugin = VotemapPlugin
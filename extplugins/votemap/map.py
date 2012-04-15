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

"""\
Module implementing strategies for picking a given number of maps out of a set of available maps.

Methods should return a list of indices for the list of available maps provided.

"""
from collections import deque
from random import shuffle


def get_n_next_maps(available_maps, n, current_indice, ignored_indices=list()):
    indices_after_current_one = deque(range(len(available_maps)))
    indices_after_current_one.rotate(0 - (int(current_indice) + 1))
    available_indices = [x for x in indices_after_current_one if x not in ignored_indices]
    return available_indices[:n]


def get_n_random_maps(available_maps, n, current_indice, ignored_indices=list()):
    indices = range(len(available_maps))
    shuffle(indices)
    indices_after_current_one = deque(indices)
    indices_after_current_one.rotate(0 - (int(current_indice) + 1))
    available_indices = [x for x in indices_after_current_one if x not in ignored_indices]
    return available_indices[:n]


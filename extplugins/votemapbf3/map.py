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

Methods should return a MapListBlock object.

"""
from collections import deque
from random import shuffle


'''
all strategies are implemented as a function with parameters :
available_maps, max_number_of_maps, current_map, ignored_maps=list()

where
- available_maps is a list of map
- max_number_of_maps is a integer
- current_map is a map
- ignored_maps is a list of map

given that map is a dict like : {'name', 'gamemode', 'num_of_rounds'}

Strategies will try to provide at least 2 maps. If necessary by not ignoring the given ignored maps.
'''

def get_n_next_maps(available_maps, max_number_of_maps, current_map, ignored_maps=list()):
    maps = deque(available_maps)
    if current_map in maps:
        while maps[0] != current_map:
            maps.rotate(-1)
        maps.rotate(-1)
    maps_set = list()
    for current_map in maps:
        if current_map not in maps_set:
            maps_set.append(current_map)
    maps_to_ignore = list(ignored_maps)
    while len(maps_set) > 2 and len(maps_to_ignore):
        try:
            target = maps_to_ignore.pop()
            maps_set.remove(target)
        except ValueError:
            pass
    return maps_set[:max_number_of_maps]


def get_n_random_maps(available_maps, max_number_of_maps, current_map, ignored_maps=list()):
    maps = list(available_maps)
    shuffle(maps)
    return get_n_next_maps(maps, max_number_of_maps, current_map, ignored_maps)


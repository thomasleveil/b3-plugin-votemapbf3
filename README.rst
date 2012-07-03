VoteMap Battlefield 3 for Big Brother Bot
=========================================


Description
-----------

This plugin brings new commands to B3 for allowing players to vote for the next map on Battlefield 3 servers.

.. image:: http://i.imgur.com/Wvxwa.png
   :alt: In-game screenshot
   :target: http://imgur.com/Wvxwa


Requirements
------------

- This plugin only works for BF3 servers
- B3 v1.8.2dev2 or later

Installation
------------

- copy the votemapbf3 directory into b3/extplugins
- copy the plugin_votemapbf3.ini config file to your config folder
- add to the plugins section of your main b3 config file::

  <plugin name="votemapbf3" config="@b3/extplugins/conf/plugin_votemapbf3.ini" />


Commands
--------

!votemap or /votemap
  Start a vote proposing maps as defined in the config. Players reply with the number of the map.

!cancelvote or /cancelvote
  Cancel current vote

!v or /v
  Display maps you can vote for

!# or /# where # is the number for a map
  Vote for one of the suggested map


Support
-------

Support is only provided on www.bigbrotherbot.net forums on the following topic :
http://bit.ly/JhIPy2



Changelog
---------

1.0
  First release

1.1
  Python 2.6 compatibility

1.1.1
  - Fixes bug that made impossible to use the random strategy to pick the map options
  - Fixes command error when the map rotation list is empty and using the !votemap command
  - Fixes bug that prevented default messages to be considered if not present in config

1.2
  - Add a new config option (maplist_file) to list the maps that can be voted in a text file
  - Fixes nextmap_display_interval that was not working at all
  - Maps options are now announced with their gamemode

1.2.1
  - Fixes bug where more than 10 vote options would not be sorted correctly before being displayed. See https://github.com/courgette/b3-plugin-votemapbf3/issues/1

1.2.2
  - Fixes bug preventing the plugin to load with B3 1.8.2


Contrib
-------

- *features* can be discussed on the `B3 forums <http://bit.ly/JhIPy2>`_
- documented and reproducible *bugs* can be reported on the `issue tracker <https://github.com/courgette/b3-plugin-votemapbf3/issues>`_
- *patches* are welcome. Send me a `pull request <http://help.github.com/send-pull-requests/>`_. It is best if your patch provides tests.

.. image:: https://secure.travis-ci.org/courgette/b3-plugin-votemapbf3.png?branch=master
   :alt: Build Status
   :target: http://travis-ci.org/courgette/b3-plugin-votemapbf3


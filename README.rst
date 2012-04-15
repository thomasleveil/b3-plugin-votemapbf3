VoteMap Battlefield 3 for Big Brother Bot
=========================================


Description
-----------

This plugin brings new commands to B3 for allowing players to vote for the next map on Battlefield 3 servers.


Requirements
------------

- This plugin only works for BF3 servers
- B3 v1.8.2dev2 or later

Installation
------------

- copy the votemap directory into b3/extplugins
- copy the plugin_votemap.ini config file to your config folder
- add to the plugins section of your main b3 config file::

  <plugin name="votemap" config="@b3/extplugins/conf/plugin_votemap.xml" />


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


Contrib
-------

- *features* can be discussed on the `B3 forums <http://bit.ly/JhIPy2>`_
- documented and reproducible *bugs* can be reported on the `issue tracker <https://github.com/courgette/b3-plugin-votemapbf3/issues>`_
- *patches* are welcome. Send me a `pull request <http://help.github.com/send-pull-requests/>`_. It is best if your patch provides tests.

.. image:: https://secure.travis-ci.org/courgette/b3-plugin-votemapbf3.png?branch=master
   :alt: Build Status
   :target: http://travis-ci.org/courgette/b3-plugin-votemapbf3


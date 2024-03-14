# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from threading import Thread, Event
from typing import List, Optional
from os.path import join, dirname, expanduser, isdir
from random import sample
from ovos_plugin_common_play import MediaType, PlaybackType
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill, ocp_search, ocp_play
from ovos_utils import classproperty
from ovos_utils.log import LOG
from ovos_utils.process_utils import RuntimeRequirements
from ovos_utils.xdg_utils import xdg_cache_home
import os
import sys
sys.path.append(os.path.abspath("/home/neon/.local/share/neon/skills/skill-local_music-mike99mac"))
from mpc_client import MpcClient
from music_info import Music_info
from util import MusicLibrary, Track

class LocalMusicSkill(OVOSCommonPlaybackSkill):
  def __init__(self, **kwargs):
    self.supported_media = [MediaType.MUSIC,
                            MediaType.AUDIO,
                            MediaType.GENERIC]
    self.library_update_event = Event()
    self.mpc_client = MpcClient("file:///mnt/usb/music/") # search for music under /mnt/usb/music
    self._music_library = None
    # self.music_dir = "/mnt/usb"   
    self.music_info = Music_info("none", "", {}, []) # music to play
    self._image_url = join(dirname(__file__), 'ui/music-solid.svg')
    self._demo_dir = join(expanduser(xdg_cache_home()), "neon", "demo_music")
    OVOSCommonPlaybackSkill.__init__(self, **kwargs)

  @classproperty
  def runtime_requirements(self):
    return RuntimeRequirements(network_before_load=False,
                             internet_before_load=False,
                             gui_before_load=False,
                             requires_internet=False,
                             requires_network=False,
                             requires_gui=False,
                             no_internet_fallback=True,
                             no_network_fallback=True,
                             no_gui_fallback=True)

  @property
  def demo_url(self) -> Optional[str]:
    # default_url = "https://2222.us/app/files/neon_music/music.zip"
    return self.settings.get("demo_url")

  @property
  def music_dir(self) -> str:
    # default_path = "/media"
    # return expanduser(self.settings.get('music_dir', ""))
    return self.music_dir

  @property
  def music_library(self):
    if not self._music_library:
      LOG.info(f"LocalMusicSkill:music_library() Initializing music library at: {self.music_dir}")
      self._music_library = MusicLibrary(self.music_dir, self.file_system.path)
    return self._music_library

    # TODO: Move to __init__ after ovos-workshop stable release
  def initialize(self):
      # TODO: add intent to update library?
      # Thread(target=self.update_library, daemon=True).start()
      pass

  def update_library(self):
    LOG.info(f"LocalMusicSkill:update_library() - can mpd auto-update?")
    self.mpc_client.mpc_update()

  def tracks_to_search_results(self, tracks: List[Track], score: int):
    LOG.info(f"LocalMusicSkill.tracks_to_search_results() match_type = {self.music_info.match_type} score = {score}")
    tracks = [{'media_type': MediaType.MUSIC,
               'playback': PlaybackType.AUDIO,
               'image': track.artwork if track.artwork else None,
               'skill_icon': self._image_url,
               'uri': track.path,
               'title': track.title,
               'artist': track.artist,
               'length': track.duration_ms,
               'match_confidence': 100} for track in tracks]
    return tracks   

  @ocp_search()
  def search_music(self, sentence, media_type=MediaType.GENERIC):
    LOG.info(f"LocalMusicSkill:search_music(): sentence = {sentence}")
    sentence = sentence.lower()            # fold to lower case

    # if first word is a playlist verb then manipulate playlists  
    first_word = sentence.split(' ', 1)[0]
    match first_word:
      case 'create'|'make'|'add'|'at'|'delete'|"i'd"|'remove'|'list'|'what': # 'add' is sometimes 'at' or I'd
        self.music_info = self.mpc_client.manipulate_playlists(sentence)
        return {'confidence':100, 'correlator':0, 'sentence':sentence, 'url':self.url} # all done

    # if track or album is specified, assume it is a song, else search for 'radio', 'internet' or 'news' requests
    song_words = ["track", "song", "title", "album", "record", "artist", "band" ]
    if "internet radio" in sentence:
      request_type = "radio"
    elif "internet" in sentence:
      request_type = "internet"
    elif any([x in sentence for x in song_words]):
      request_type = "music"
    elif "radio" in sentence:
      request_type = "radio"
    elif "n p r" in sentence or "news" in sentence:
      request_type = "news"
    elif "playlist" in sentence:
      request_type = "playlist"
    else:
      request_type = "music"

    # search for music in (1) library, on (2) Internet radio, on (3) the Internet, (4) in a playlist or (5) play NPR news
    LOG.info(f"LocalMusicSkill:search_music(): request_type = {request_type}")
    match request_type:
      case "music":                        # if not found in library, search internet
        self.music_info = self.mpc_client.search_library(sentence)
        LOG.info(f"LocalMusicSkill:search_music() match_type = {self.music_info.match_type}")
        if self.music_info.match_type == "none": # music not found in library
          self.sentence = sentence
          LOG.info(f"LocalMusicSkill:search_music(): not found in library - searching Internet")
          self.music_info.mesg_file = "searching_internet"
          self.music_info.mesg_info = {"sentence": sentence}
          self.speak_lang(self.skill_base_dir, self.music_info.mesg_file, self.music_info.mesg_info)
          self.music_info = self.mpc_client.search_internet(self.sentence) # search Internet as fallback
      case "radio":
        self.music_info = self.mpc_client.parse_radio(sentence)
      case "internet":
        self.music_info = self.mpc_client.search_internet(sentence)
      case "playlist":
        self.music_info = self.mpc_client.get_playlist(sentence)
      case "news":
        self.music_info = self.mpc_client.search_news(sentence)
    if self.music_info.tracks != None:     # found music
      LOG.info("LocalMusicSkill:search_music(): found tracks or URLs - calling tracks_to_search_results()")
      tracks = self.tracks_to_search_results(self.music_info.tracks, 100)
      return tracks
    else:                                  # found no music or error
      LOG.info(f"LocalMusicSkill:search_music() did not find music: mesg_file = {self.music_info.mesg_file} mesg_info = {self.music_info.mesg_info}")
      return None
  
  @ocp_play()
  def media_play(self, msg):
    """
    Either music has been found, a playlist operation finished, or an error message has to be spoken
    """
    LOG.info(f"LocalMusicSkill.media_play() match_type = {self.music_info.match_type}")
    if self.music_info.match_type == "none": # no music was found
      self.log.debug("MpcSkill.media_play() no music found")
      self.speak_lang(self.skill_base_dir, self.music_info.mesg_file, self.music_info.mesg_info)
      return None
    elif self.music_info.match_type == "playlist_op": # playlist operation - no music, just speak message
      self.log.debug("MpcSkill.media_play() speak results of playlist request")
      self.speak_lang(self.skill_base_dir, self.music_info.mesg_file, self.music_info.mesg_info)
      return None
    elif self.music_info.match_type != "playlist": # playlists are already queued up
      self.mpc_client.mpc_cmd("clear")     # stop any media that might be playing
      for next_url in self.music_info.tracks_or_urls:
        self.log.debug(f"MpcSkill.media_play() adding URL to MPC queue: {next_url}")
        cmd = f"add {next_url}"
        self.mpc_client.mpc_cmd(cmd)
    elif self.music_info.match_type == "playlist":
      self.mpc_client.mpc_cmd("random on") # shuffle tracks
    if self.music_info.mesg_file == None:  # no message
      self.start_music()
    else:                                  # speak message and pass callback
      self.speak_lang(self.skill_base_dir, self.music_info.mesg_file, self.music_info.mesg_info, self.start_music)

  

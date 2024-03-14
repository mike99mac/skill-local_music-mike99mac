#
# This code is distributed under the Apache License, v2.0 
#
class Music_info:
  match_type = ""                  # album, artist, empty_playlist, next, none, playlist_op, playlist, prev, radio or song 
  mesg_file = ""                   # if mycroft has to speak first
  mesg_info = {}                   # values to plug in
  tracks = []                      # list of Track objects
  def __init__(self, match_type, mesg_file, mesg_info, tracks):
    self.match_type = match_type
    self.mesg_file = mesg_file
    self.mesg_info = mesg_info
    self.tracks = tracks

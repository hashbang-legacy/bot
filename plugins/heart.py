# -*- coding: utf-8 -*-

import api
@api.onPrivmsg()
def heartify(src, msg, dst):
  if "<3" in msg:
    api.privmsg(dst, msg.replace("<3", u'{C5}♥{}'))

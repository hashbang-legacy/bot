import api
from util.name import getNames

@api.onCommand("name")
def onName(sender, args, chan):
  api.privmsg(chan, str(getNames(chan)))

import api
from collections import defaultdict

""" Keeping track of nicks in a channel """
__map = defaultdict(set)
@api.onNames()
def __printNames(channel, names):
  __map[channel].update(names)
  #api.privmsg(channel, str(names))

@api.onJoin()
def __joined(name, channel):
  __map[channel].add(name)

@api.onPart()
def __parted(name, channel, msg):
  __map[channel].remove(name)

def getNames(channel):
  return list(__map[channel])


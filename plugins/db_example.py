import api
import db
# Create a shelve.
# also seed it with initial data
d = db.Shelve({
  "loads": 0
})

d["loads"] += 1

loads = d["loads"]

@api.onCommand("loads")
def printLoads(sender, args, chan):
  api.privmsg(chan, "I've been restarted %s times!" % loads)


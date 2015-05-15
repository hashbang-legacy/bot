import api
import datetime
from collections import defaultdict
import db

store = db.Shelve({
  "alarms":{},
  "blocked":set()})
messages = store["alarms"]
blocked = store["blocked"]


"""
Minor interesting point. if you tell yourself a message, then the
order of api.onPrivmsg and api.onCommand fire matters.

As of the time of this writing, they are executed in order of
decorator application. activity calls its decorator before onTell
so privmsg is handled, then onTell.

Meaning you can send yourself a !tell, that wont be repeated until
your next message sent somewhere the bot can see.
"""

@api.onPrivmsg()
def activity(who, what, where):
    if who in messages:
        for msg in messages[who]:
            api.privmsg(who, msg)
        del messages[who]
        store["alarms"] = messages

@api.onCommand("tell")
def onTell(who, args, where):
    if args == "off":
        blocked.add(who)
        store["blocked"] = blocked
        api.privmsg(who, offMessage)
        return

    if args == "on":
        blocked.remove(who)
        store["blocked"] = blocked
        api.privmsg(who, onMessage)
        return

    nick, msg = args.split(" ", 1)
    if nick in store["blocked"]:
        api.privmsg(who,
            disabledMessage.format(nick))
        return

    when = getTime()
    msg = when + " " + who +": " + msg
    if nick not in messages:
      messages[nick] = []
    messages[nick].append(msg)
    store["alarms"] = messages


offMessage = "!tell's are {RED}disabled{} for you. Use '!tell on' to turn them back on"
onMessage = "!tell's are {GREEN}enabled{} for you. Use '!tell off' to disable them"
disabledMessage = "{} has {{RED}}disabled{{}} !tells. Please use memoserv or a PM instead"


# This is hard to test correctly with actual time
# Factor it out so that the test can replace it.
def getTime():
    return datetime.datetime.now().strftime("%H:%M:%S %m/%d/%y")



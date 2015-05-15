import api

@api.onPrivmsg()
def onLine(sender, message, target):
  if message=="\\o/":
    api.privmsg(target, "YAY")
    api.privmsg(target, "/ \\")



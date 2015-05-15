import api

lastLines = {}
@api.onPrivmsg()
def onLine(sender, message, target):
  prevLine = lastLines.get(target, "")
  if prevLine == message:
    api.privmsg(target, message)
    message = ""
  lastLines[target] = message

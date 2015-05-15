import api
import datetime

@api.onCommand("date")
def printDate(sender, args, replyTo):
  now = datetime.datetime.now()
  api.privmsg(replyTo, now.strftime("%H:%M:%S %A. %B(%m) %d %Y"))



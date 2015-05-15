import api
print("Repeat loaded")
@api.onCommand("repeat")
def repeatLine(sender, msg, to):
  api.privmsg(to, msg)

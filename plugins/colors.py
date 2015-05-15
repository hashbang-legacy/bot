import api

colors = []
for i in range(16):
  s = str(i)
  colors.append("{{C{}}}{}".format(s,s))
message = " ".join(colors)

@api.onCommand("colors")
def showColors(src, args, chan):
  api.msg(chan, message)

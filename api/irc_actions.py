from api.handlers import emitEvent
def raw(line):
  emitEvent("sendline", line)

def rawf(line, *args):
  raw(line.format(*args))

def notice(target, message):
  rawf(u"NOTICE {} :{}", target, message)

def msg(target, message):
  rawf(u"PRIVMSG {} :{}", target, message)
privmsg = msg

def join(chan):
  rawf(u"JOIN {}", chan)

def ctcp(who, cmd, val):
  if val:
    cmd += " " + val

  notice(who, u"\x01{}\x01".format(cmd))

from api.handlers import register
import re

# Decorators
# Lower level - works on all lines of irc
def onRawLine():
  def decorator(func):
    register("line", func)
    return func
  return decorator

def onRegex(expr, flags=0, search=False):
  # search - search or match, defaults to match.
  matcher = re.compile(expr, flags)
  matchcmd = matcher.search if search else matcher.match
  def decorator(func):
    @onRawLine()
    def handler(line):
      match = matchcmd(line)
      #print("Checking " + line + " against " + expr + " " + str(match is not None))
      if not match:
        return
      func(match)
    return handler
  return decorator

# protocol level - works of each interesting message type
def __messageRegex(command):
    return "^:(.*?)!.*?{} (.*?) ?:(.*)$".format(command)

":snail!snail@#!-D1E8CCF0.hsd1.ca.comcast.net PART #!social :testing Part"
":snail!snail@#!-D1E8CCF0.hsd1.ca.comcast.net JOIN :#!social"

":someNick!a@#!-D1E8CCF0.hsd1.ca.comcast.net JOIN :#test"
":lon1.irc.hashbang.sh 353 someNick = #test :someNick snail @viaken "
":lon1.irc.hashbang.sh 366 someNick #test :End of /NAMES list."

def onJoin():
  def decorator(func):
    @onRegex(__messageRegex("JOIN"))
    def handler(match):
      sender, target, message = match.groups()
      func(sender, message)
    return handler
  return decorator

def onPart():
  def decorator(func):
    @onRegex(__messageRegex("PART"))
    def handler(match):
      sender, chan, msg = match.groups()
      func(sender, chan, msg)
    return handler
  return decorator

def onNames():
  def decorator(func):
    @onRegex("^[^ ]+ 353 [^:]+ (.*?) :(.*)$")
    def handler(match):
      channel, names = match.groups()
      names = names.strip().split()
      func(channel, names)
    return handler
  return decorator

def onPrivmsg():
  def decorator(func):
    @onRegex(__messageRegex("PRIVMSG"))
    def handler(match):
      sender, target, message = match.groups()

      if target[0]!='#':
        target = sender

      func(sender, message, target)
    return handler
  return decorator
onMsg = onPrivmsg

def onInvite():
  def decorator(func):
    @onRegex(__messageRegex("INVITE"))
    def handler(match):
      sender, target, channel = match.groups()
      func(sender, channel)
    return handler
  return decorator


# high level - works on only specifically interesting events
def onCommand(command=None, split=False):
  """
  command - string to match to run this command
  split - whther to return the args as a string(False)
          or the parsed list (True).

  @cmd("date", split=True)
  def date(sender, args, target):
  """

  hook = [command, split]
  def decorator(func):
    @onPrivmsg()
    def commandHandler(who, what, where):

      if re.match("^!" + command + "(\\s.*|)$", what) is None:
        return

      if split:
        args = what.split(" ")[1:]
      else:
        args = ""
        if " " in what:
          args = what.split(" ",1)[1]

      func(who, args, where)
    return commandHandler
  return decorator

def onCTCP(command):
  def decorator(func):
    @onPrivmsg()
    def commandHandler(who, what, where):
      match = re.match("\x01([^ ]+) ?(.*?)\x01", what)
      if match is None:
        return

      cmd, args = match.groups()
      if command == cmd:
        func(who, cmd, args)
    return commandHandler
  return decorator
# add onSchedule(seconds)


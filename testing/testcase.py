import unittest
import api.handlers

# Replace db's with dict-backed shelves instead of files.
import db
db.shelve_opener = lambda name:{}
db.sqlite3_opener = lambda name:db.sqlite3.connect(":memory:")



channel = "#testchan"

class User:
  # User assertions come in the form:
  # assert[No][Pm|Msg]
  # with the 'No' the method takes no arguments
  # and asserts that the associated 'buffer' is empty.
  # Pm is for private messages from the bot.
  # Msg is for messages to the testing channel from the bot.
  #
  # If User1 says something in the testing channel, it does **NOT**
  # show up for User2 who's also in the channel.

  def __init__(self, tester, nick):
    """
    tester should be an instance of unittest.TestCase,
            or something that has assertion methods on it.
    nick is the name of this user (must be unique)
    """

    self.tester = tester
    self.nick = nick
    self.pms = []
    self.msgs = []

  def clear(self):
    self.pms.clear()
    self.msgs.clear()

  def receive(self, message, pm):
    if pm:
        self.pms.append(message)
    else:
        self.msgs.append(message)

  def say(self, message):
    api.handlers.emitEvent("line",
    ":{}!username@hostname PRIVMSG {} :{}".format(
      self.nick,
      channel,
      message
      ))

  def assertNoPm(self):
    self.tester.assertEqual(self.pms, [])

  def assertPm(self, expected):
    self.tester.assertTrue(len(self.pms) > 0)

    actual = self.pms.pop(0)
    self.tester.assertEqual(actual, expected)

  def assertNoMsg(self):
    self.tester.assertEqual(self.msgs, [])

  def assertMsg(self, expected):
    self.tester.assertTrue(len(self.msgs) >0)
    actual = self.msgs.pop(0)
    self.tester.assertEqual(actual, expected)


class TestCase(unittest.TestCase):

  # When the bot sends a line during this test:
  def botSent(self, line):
    if line.startswith("PRIVMSG"):
      _, target, message = line.split(" ", 2)
      message = message[1:] #Remove the ':' prefix.

      if target == channel:
        self.alice.receive(message, False)
        self.bob.receive(message, False)
        return

      if target == 'alice':
        self.alice.receive(message, True)
        return

      if target == 'bob':
        self.bob.receive(message, True)
        return

    self.fail("Test framework failure. Unhandled line:" + line)


  def setUp(self):
    self.alice = User(self, 'alice')
    self.bob = User(self, 'bob')
    api.handlers.register("sendline", self.botSent)

  def tearDown(self):
    api.handlers.unregister("sendline", self.botSent)

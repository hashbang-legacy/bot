from testing.testcase import TestCase
from . import tell

# Replace getTime with something that we can test with.
tell.getTime = lambda: "<TIME>"

class Test(TestCase):
  def testTell(self):
    self.alice.say("!tell bob hello")
    self.bob.assertNoPm()
    self.bob.say("message")
    self.bob.assertPm("<TIME> alice: hello")

  def testTellOff(self):
    self.bob.say("!tell off")
    self.bob.assertPm(tell.offMessage)
    self.alice.say("!tell bob hello")
    self.alice.assertPm(tell.disabledMessage.format("bob"))

  def testTellOn(self):
    self.bob.say("!tell off")
    self.bob.clear()

    self.bob.say("!tell on")
    self.bob.assertPm(tell.onMessage)
    self.testTell()



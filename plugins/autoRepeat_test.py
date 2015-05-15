from testing.testcase import TestCase
from . import autoRepeat

class TestRepeat(TestCase):
  def test_repeat(self):
    self.alice.say("repeat test")
    self.alice.assertNoMsg()
    self.alice.say("repeat test")
    self.alice.assertMsg("repeat test")
    self.alice.say("repeat test")
    self.alice.assertNoMsg()


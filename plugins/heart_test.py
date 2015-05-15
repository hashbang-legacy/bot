from testing.testcase import TestCase
from . import heart

class TestHeart(TestCase):
  def test_without_heart(self):
    self.alice.say("heart test without heart")
    self.alice.assertNoMsg()

  def test_with_heart(self):
    self.alice.say("heart test with <3")
    self.alice.assertMsg("heart test with {C5}\u2665{}")


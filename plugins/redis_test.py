from testing.testcase import TestCase
from . import redis

class TestRedis(TestCase):
  def test_with_heart(self):
    self.alice.say("!redis set x 3")
    self.alice.assertMsg(redis.okFmt.format(True))
    self.alice.say("!redis get x")
    self.alice.assertMsg(redis.okFmt.format(b'3'))
    self.alice.say("!redis incr x")
    self.alice.assertMsg(redis.okFmt.format(4))


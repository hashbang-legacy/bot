from testing.testcase import TestCase
from . import math

class TestMath(TestCase):
  def test_simple(self):
    self.alice.say("%1+2")
    self.alice.assertMsg("{GREEN}3.0")

  def test_error(self):
    self.assertRaises(Exception,
        self.alice.say,
        "%1+")
    self.alice.assertMsg(
        "{GREEN}1+{RED}<Incomplete expression>{GREEN}")

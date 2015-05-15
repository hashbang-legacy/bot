from testing.testcase import TestCase
from unittest.mock import patch
from io import StringIO
from . import eval

# Make the commands blocking.
eval.bg = lambda cmd,*args:cmd(*args)


class TestEval(TestCase):

  @patch('sys.stdout', new_callable=StringIO)
  def test_echo(self, stdout):
    self.alice.say("!eval echo test")
    self.alice.assertMsg(eval.stdoutFmt.format("test"))

    #TODO fix this assertion
    self.assertNotEqual(
        stdout.getvalue(),
        "")

  @patch('sys.stdout', new_callable=StringIO)
  def test_bad_lang(self, stdout):
    self.alice.say("!eval ../bad.sh muahaha")
    self.alice.assertMsg(eval.usage)

    #TODO fix this assertion
    self.assertNotEqual(
        stdout.getvalue(),
        "")

  @patch('sys.stdout', new_callable=StringIO)
  def test_no_bash_evaluation(self, stdout):
    self.alice.say("!eval echo *")
    self.alice.assertMsg(eval.stdoutFmt.format("*"))
    # Should be '*' not a directory list.

    #TODO fix this assertion
    self.assertNotEqual(
        stdout.getvalue(),
        "")

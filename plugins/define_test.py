from testing.testcase import TestCase
from . import define

# Replace getTime with something that we can test with.
define.define = lambda phrase:[
  {"text": "Meaning 1"},
  {"text": "Meaning 2"},
  {"text": "Meaning 3"},
]

class Test(TestCase):
  def test_define(self):
    self.alice.say("!gd bob")
    self.alice.assertMsg(
      define.definitionFmt.format(
        num = 1,
        tot = 3,
        term = "bob",
        definition = "Meaning 1"))

  def test_define_valid_arg(self):
    self.alice.say("!gd 2 bob")
    self.alice.assertMsg(
      define.definitionFmt.format(
        num = 2,
        tot = 3,
        term = "bob",
        definition = "Meaning 2"))

  def test_define_invalid_arg(self):
    self.alice.say("!gd 10 bob")
    self.alice.assertMsg(
      define.invalidArg.format(
        tot = 3,
        term = "bob"
      ))

  def test_define_no_args(self):
    self.alice.say("!gd")
    self.alice.assertMsg(define.usage)

    self.alice.say("!gd ")
    self.alice.assertMsg(define.usage)

  def test_no_results(self):
    old = define.define
    define.define = lambda p:[]
    self.alice.say("!gd noResults")
    self.alice.assertMsg(define.noDefinitions.format(term="noResults"))
    define.define = old

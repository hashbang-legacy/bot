from testing.testcase import TestCase
from unittest.mock import patch
from . import url



class TestUrl(TestCase):

  @patch('plugins.url.getTitle')
  @patch('plugins.url.shorten')
  def test_with_both(self, shorten, title):
    shorten.return_value = "SHORTURL"
    title.return_value = "TITLE"
    self.alice.say("http://longurl.com/withmoreurl")
    self.alice.assertMsg(url.outputFmt.format(
      short = url.shortFmt.format("SHORTURL"),
      delim = url.delim,
      title = url.titleFmt.format("TITLE")))


  @patch('plugins.url.getTitle')
  @patch('plugins.url.shorten')
  def test_only_title(self, shorten, title):
    title.return_value="Short.com title"
    self.alice.say("http://short.com")
    shorten.assert_has_calls([]) # no calls to shorten.
    self.alice.assertMsg(url.outputFmt.format(
      short = "",
      delim = "",
      title = url.titleFmt.format("Short.com title")))


  @patch('plugins.url.getTitle')
  @patch('plugins.url.shorten')
  def test_only_short(self, shorten, title):
    shorten.return_value = "SHORTURL"
    title.return_value = ""

    self.alice.say("http://someUrlWithoutATitle.com/longUrl")
    self.alice.assertMsg(url.outputFmt.format(
      short = url.shortFmt.format("SHORTURL"),
      delim ="",
      title =""
    ))

  def test_neither(self):
    self.alice.say("No urls here")
    self.alice.assertNoMsg()


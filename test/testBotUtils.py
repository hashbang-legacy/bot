import unittest
from unittest.mock import MagicMock

from bot import utils

class ParseMsg(unittest.TestCase):
    # http://tools.ietf.org/html/rfc2812

    def testPing(self):
        line = "PING foo.bar"
        self.assertEqual(
            utils.parsemsg(line),
            {'prefix': '',
             'command': 'PING',
             'args': ['foo.bar'],
             'raw': line})

# Create a mock socket that will act as the connection to the irc server
def mockServer(outputs):
    sock = MagicMock()
    def onRecv(count):
        if not outputs:
            return b''
        return outputs.pop(0).encode('utf-8')
    sock.recv.side_effect = onRecv
    return sock

class MessageIterator(unittest.TestCase):

    def testMultipleLinesInData(self):
        sock = mockServer(["line1\r\nline2\r\n"])

        for lineno, line in enumerate(utils.messageIterator(sock)):
            if lineno == 0:
                self.assertEqual(line['raw'], "line1")
            elif lineno == 1:
                self.assertEqual(line['raw'], "line2")
            else:
                self.fail("Only 2 messages should be parsed from input data")

    def testPartialLineInData(self):
        sock = mockServer(["line"]) # missing \r\n. so it's not complete.
        for line in utils.messageIterator(sock):
            self.fail("Should not return incomplete lines")

    def testMultiPartData(self):
        sock = mockServer(["line", "1\r\nli", "ne2\r\n"])
        for lineno, line in enumerate(utils.messageIterator(sock)):
            if lineno == 0:
                self.assertEqual(line['raw'], "line1")
            elif lineno == 1:
                self.assertEqual(line['raw'], "line2")
            else:
                self.fail("Only 2 messages should be parsed from input data")




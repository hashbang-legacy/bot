
import unittest
from unittest.mock import MagicMock, patch

from bot import Bot

def createBot(config):
    """ Creates a bot that is connected to a MagicMock socket.
    returns (bot, socket)
    """
    sock = MagicMock()
    with patch('socket.socket') as socket:
        socket.return_value = sock
        bot = Bot(config)

    return (bot, sock)

class BotConstruction(unittest.TestCase):

    def testEmptyConfig(self):
        # Empty config should raise an error
        self.assertRaises(KeyError, createBot, {})

    def testMinimalConfig(self):
        # Host is all that's technically required.
        # defaults to port 6667
        bot,sock = createBot({'host':'someHost'})
        sock.connect.assert_called_with(('someHost', 6667))

    def testHostPortConfig(self):
        bot,sock = createBot({'host':'someOtherHost', 'port': 1234})
        sock.connect.assert_called_with(('someOtherHost', 1234))



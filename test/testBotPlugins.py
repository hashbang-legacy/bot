import unittest
import time
from unittest.mock import Mock
from bot.plugins import ScriptPlugin

class ScriptPluginTest(unittest.TestCase):
    
    def __testScriptExit0Unloads(self):
        bot = Mock()
        plugin = ScriptPlugin("../test/plugins/exit")(bot)
        plugin.handleMessage({"exit": 0})
        time.sleep(0.1)
        bot.unload.assert_called_with()

    def testScriptExitNon0Reloads(self):
        bot = Mock()
        plugin = ScriptPlugin("../test/plugins/exit")(bot)
        plugin.timeout = .1
        plugin.handleMessage({"exit": 1})

        #TODO This should not require a sleep. 
        time.sleep(.2)
        self.assertFalse(bot.unload.called) 
        
        plugin.handleMessage({"exit": 0})
        time.sleep(.1)
        bot.unload.assert_called_with()


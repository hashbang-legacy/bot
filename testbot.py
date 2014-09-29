import unittest
from unittest.mock import Mock
from bot import *

class TestPluginManager(unittest.TestCase):
    def setUp(self):
        self.handler = Mock()
        self.pm = PluginManager(self.handler)

    def test_end_calls_plugin_end(self):
        plugin = Mock()
        plugin2 = Mock()
        self.pm.loadPlugin("p1", plugin)
        self.pm.loadPlugin("p2", plugin2)
        self.pm.end()
        plugin.end.assert_called_with()
        plugin2.end.assert_called_with()


    def test_reload_plugin_kills_old(self):
        plugin = Mock()
        plugin2 = Mock()
        self.pm.loadPlugin("plugin", plugin)
        self.pm.loadPlugin("plugin", plugin2)

        plugin.end.assert_called_with()

    def test_hello_world_plugin(self):
        self.pm.handlePluginMessage({
            'action': 'plugin',
            'method': 'load',
            'name': 'test',
            'code': "print(json.dumps({"
                +"'action':'message',"
                +"'channel':'#test',"
                +"'message':'a'}))"
            })
        self.pm.handleMessage({})
        import time
        time.sleep(.1)
        self.handler.assert_called_once_with({
            'action': 'message',
            'channel': '#test',
            'message': 'a'
            })
    def test_false(self):
        #self.assertTrue(False)
        pass


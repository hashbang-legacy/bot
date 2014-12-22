from .plugins import ScriptStarterPlugin
from .utils import log, parsemsg, connect, messageIterator

class Bot:
    def __init__(self, config):
        self.sock = connect(config)
        self.authenticate(config)
        self.plugins = {}
        self.toUnload = []
        self.toLoad = []

    def send(self, message, *args):
        """ Send a message to the connected server.
        Accepts *args as the message can be formatted.

        This method adds the trailing newlines"""
        data = message.format(*args).encode('utf-8')
        self.sock.send(data)
        self.sock.send(b"\r\n")

    def authenticate(self, config):
        """ Handshake with the IRC server. If there's a password, use it."""
        if "password" in config:
            self.send("PASS {}", config["password"])

        self.send("NICK {}", config.get("nick", "unnamedBot"))
        self.send("USER a b c d :e")

    def loop(self):
        """ Main loop of the bot.
        Dispatch each message to each loaded plugin.
        Handle any plugin changes (load/unloads).
        """
        for message in messageIterator(self.sock):
            for uuid, plugin in self.plugins.items():
                plugin.handleMessage(message)

            while self.toLoad:
                self.__loadPlugin(self.toLoad.pop())

            while self.toUnload:
                del self.plugins[self.toUnload.pop()]


        for key in list(self.plugins):
            del self.plugins[key]

    def loadPlugin(self, plugin_cls):
        """ Schedule a plugin to be loaded """
        print("LOAD: " + str(plugin_cls))
        self.toLoad.append(plugin_cls)

    def __loadPlugin(self, plugin_cls):
        """ Actually load a plugin. """

        import uuid

        key = uuid.uuid4()
        instance = plugin_cls(Bot.API(self, key))

        self.plugins[key] = instance
        return key

    def unloadPlugin(self, key):
        """ Schedule a plugin to be unloaded """
        self.toUnload.append(key)

    class API:
        # Class given to plugins to interact with the bot.
        def __init__(self, bot, key):
            self.__bot = bot
            self.__key = key

        # Plugin management
        def loadPlugin(self, plugin):
            """ Tell the bot to load another plugin."""
            self.__bot.loadPlugin(plugin)

        def unload(self):
            """ Tell the bot to unload the current plugin"""
            self.__bot.unloadPlugin(self.__key)

        # Irc commands
        def privmsg(self, channel, message):
            """ Send a PRIVMSG to a channel (or nick) """
            self.quote("PRIVMSG {} :{}", channel, message)

        def quote(self, line, *args):
            """ Send an arbitrary message to the server, this message
            can have optional formatting to it. """
            self.__bot.send(line, *args)

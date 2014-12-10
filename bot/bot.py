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
        data = message.format(*args).encode('utf-8')
        self.sock.send(data)
        self.sock.send(b"\r\n")

    def authenticate(self, config):
        if "password" in config:
            self.send("PASS {}", config["password"])

        self.send("NICK {}", config.get("nick", "unnamedBot"))
        self.send("USER a b c d :e")

    def loop(self):
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
        print("LOAD: " + str(plugin_cls))
        import uuid
        if type(plugin_cls) == uuid.UUID:
            i = 0;
            i/=0;
        self.toLoad.append(plugin_cls)

    def __loadPlugin(self, plugin_cls):
        import uuid

        key = uuid.uuid4()
        instance = plugin_cls(Bot.API(self, key))

        self.plugins[key] = instance
        return key

    def unloadPlugin(self, key):
        self.toUnload.append(key)

    class API:
        # Class given to plugins to interact with the bot.
        def __init__(self, bot, key):
            self.__bot = bot
            self.__key = key

        # Plugin management
        def loadPlugin(self, plugin):
            self.__bot.loadPlugin(plugin)

        def unload(self):
            self.__bot.unloadPlugin(self.__key)

        # Irc commands
        def privmsg(self, channel, message):
            self.quote("PRIVMSG {} :{}", channel, message)

        def pong(self, server):
            self.quote("PONG {}", server)

        def quote(self, line, *args):
            self.__bot.send(line.format(*args))

import pprint
import socket
import json

from plugins import CodePlugin
from utils import log

def parsemsg(line):
    """Breaks a message from an IRC server into its prefix, command, and
    arguments. Returns a dict with those (as well as 'raw' for original text)
    Taken from twisted irc.
    """
    prefix = ''
    trailing = []
    if not line:
        return {}
    s = line
    if s[0] == ':':
        prefix, s = s[1:].split(' ', 1)
    if s.find(' :') != -1:
        s, trailing = s.split(' :', 1)
        args = s.split()
        args.append(trailing)
    else:
        args = s.split()
    command = args.pop(0)
    return {'prefix':prefix, 'command':command, 'args':args, 'raw':line}


class PluginManager(object):

    def __init__(self, handler):
        self.handler = handler
        self.plugins = {}

    def unloadPlugin(self, name):
        if name in self.plugins:
            log("PluginManager End of {}", name)

            self.plugins[name].end()

            del self.plugins[name]

    def loadPlugin(self, name, handler, code=None):

        log("Loading plugin {} into {}", name, self.plugins)

        if name in self.plugins:
            self.unloadPlugin(name)

        if not code: # Use name as path and load code.
            code = open(name).read()

        plugin = CodePlugin(handler, name, code)

        self.plugins[name] = plugin

    def end(self):
        """ shutdown the plugin manager """
        for plugin in self.plugins.values():
            plugin.end()

    def handleMessage(self, obj):
        """ Handle messages from irc in the form of a dict """
        for plugin in list(self.plugins.values()):
            plugin.handleMessage(obj)

    def handlePluginMessage(self, obj):
        if obj.get("action", "") == "plugin":

            method = obj.get('method', '')
            name = obj.get('name', '')
            code = obj.get('code', None)

            #TODO: error handling for no method/name

            if method == "load":
                log("handlePluginMessage Code: {}", code.replace("\\n", "\n"))

                self.loadPlugin(name, self.handlePluginMessage, code=code)

            elif method == "unload":
                self.unloadPlugin(name)
        else:
            self.handler(obj)

def start():
    hostport = ('og.hashbang.sh', 4445)
    nick = 'brokens_test'
    password = 'hashbangbot:password'

    sock = socket.socket()
    sock.connect(hostport)

    def send(message, *args):
        data = message.format(*args).encode('utf-8')
        sock.send(data + b"\r\n")

    # Handshake
    if password:
        send("PASS {}", password)
    send("NICK {}", nick)
    send("USER a b c d :e")

    def handler(obj):
        action = obj.get("action", "")
        if action == "message":
            send("PRIVMSG {} :{}", obj['channel'], obj['message'])

    pm = PluginManager(handler)
    pm.loadPlugin('startup.sh', handler=pm.handlePluginMessage)

    # main loop
    read = ""
    try:
        while True:
            data = sock.recv(1024)
            read += data.decode('utf-8')
            lines = read.split("\r\n")
            lines, read = lines[:-1],lines[-1]
            for line in lines:
                line = parsemsg(line)

                if line['command'] == 'PING':
                    send("PONG {}", line['args'][0])

                pm.handleMessage(line)
    except KeyboardInterrupt:
        log("END")
        pm.end()

if __name__ == "__main__":
    try:
        start()
    except:
        print("Exceptional exit:")
        raise
    print("Regular Exit")

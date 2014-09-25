import socket
import multiprocessing
from util import *

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

class CodePlugin:
    def __init__(self, handler, code):
        print("New code plugin:", code)
        pass
    def handleMessage(self, obj):
        pass
    def end(self):
        pass

class DebugPlugin:
    def __init__(self, handler):
        """
        handler(obj) - pass a message back up through the bot
                     - obj can be an irc reply, or a plugin command
        """
        self.handler = handler
        self.seen_mode_line = False
    def handleMessage(self, obj):
        """ obj - irc message as dict """
        if obj.get("command","") == "MODE":
            self.seen_mode_line = True
        if self.seen_mode_line:
            self.handler({
                "action":"message",
                "channel":"#test",
                "message": json.dumps(obj)})

    def end(self):
        return

class PluginLoader:
    def __init__(self, handler):
        self.handler = handler

    def handleMessage(self, obj):
        if obj.get('command','') == 'PRIVMSG':
            line = obj['args'][1].split(" ", 3)
            if line[0] == "!plugin" && len(line) >= 3: # ['!plugin', '[un]load', 'name'] + optional code
                name = line[2]
                if line[1] == "load":
                    code = line[3]
                    self.handler({
                        "action": "plugin",
                        "method": "load",
                        "code": code,
                        "name": name})
                elif line[1] == "unload":
                    self.handler({
                        "action": "plugin",
                        "method": "unload",
                        "name": name})

        self.handler(obj)

import json
class PluginManager:
    def __init__(self, handler):
        self.handler = handler
        self.plugins = {}

    def unloadPlugin(self, name):
        if name in self.plugins:
            plugin = self.plugins[name]
            plugin.end()
            print("End of", name)
            del self.plugins[name]

    def loadPlugin(self, name, plugin):
        if name in self.plugins:
            self.unloadPlugin(name)
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
        print("Plugin manager:")
        pprint.pprint(obj)
        if obj.get("action","") == "plugin":
            method = obj["method"]
            name = obj["name"]
            if method == "load":
                self.loadPlugin(name,
                        CodePlugin(self.handlePluginMessage, obj["code"]))
            elif method == "unload":
                self.unloadPlugin(name)
        else:
            self.handler(obj)

import pprint
i = 30
def start():
    hostport = ('localhost', 4445)
    nick = '[bot]'
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

    # setup plugin manager

    def handler(obj):
        print("Plugin output:")
        pprint.pprint(obj)

        global i
        i = i -1
        if i > 0:
            print("skipped",i)
            return

        action = obj.get("action", "")
        if action == "message":
            send("PRIVMSG {} :{}", obj['channel'], obj['message'])


    pm = PluginManager(handler)
    pm.loadPlugin("debug", DebugPlugin(pm.handlePluginMessage))
    pm.loadPlugin("", PluginLoader(pm.handlePluginMessage))
    # main loop
    read = ""
    while True:
        data = sock.recv(1024)
        read += data.decode('utf-8')
        lines = read.split("\r\n")
        lines, read = lines[:-1],lines[-1]
        for line in lines:
            print(">> {}".format(line))
            line = parsemsg(line)

            if line['command'] == 'PING':
                send("PONG {}", line['args'][0])

            pm.handleMessage(line)


start()
print("Exit")






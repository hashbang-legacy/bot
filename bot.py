import socket
import subprocess
import threading

def log(msg, *args):
    msg = msg.format(*args) +" "
    first, rest = msg.split(" ",1)
    print("\033[33m{}\033[0m {}".format(first, rest))

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
    """ Keep a singleton select loop that runs on a map of fileno->CodePlugins
    """
    __ID = 0
    def __init__(self, handler, name, code):
        CodePlugin.__ID += 1
        name += str(CodePlugin.__ID)
        log("[CodePlugin] New code plugin:\n[{}]", name)
        self.handler = handler
        self.name = name
        self.path = "/dev/shm/" + name
        log("Opening {}", self.path)
        f = open(self.path, "w")
        f.write(code)
        f.close()
        log("Closing {}", self.path)
        self.running = False
        self.start()

    def start(self):
        self.proc = subprocess.Popen(["/usr/bin/env", "python", "-u",
            self.path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd = "/dev/shm/")

        def readThread():
            self.running = True
            while self.running:
                log("{} waiting", self.name)
                line = self.proc.stdout.readline().decode('utf-8')
                log("{} -> {}", self.name, line)
                if not line:
                    log("Plugin {} returned an empty line, polling", self.name)
                        # if running is true, then it was the script that quit
                        # if running is false, then we've called 'end'
                        #   and then the terminate caused the process exit
                    self.proc.poll()
                    if self.proc.returncode is not None:
                        log("Plugin {} died. Exit: {}", self.name, self.proc.returncode)
                        self.end()
                else:
                    line = line.strip()
                    try:
                        self.handler(json.loads(line))
                    except:
                        self.handler({"action":"message",
                            "channel":"#test",
                            "message": "Plugin {} output invalid json: {}"
                                        .format(self.name, line)})
        self.thread = threading.Thread(target=readThread)
        self.thread.start()
        log("started {}".format(self.name))

    def handleMessage(self, obj):
        try:
            self.proc.poll()
            if self.proc.returncode is not None:
                self.start()

            #log("Sending {} to {}", obj, self.name)
            log("Sending to {}", self.name)
            self.proc.stdin.write(json.dumps(obj).encode('utf-8') + b"\n")
            self.proc.stdin.flush()
        except:
            self.restart()

    def end(self):
        log("{} Ending", self.name)
        self.running = False
        try:
            self.proc.terminate()
            self.proc.wait()
        except:pass

        if threading.currentThread() != self.thread:
            self.thread.join()

        log("{} Ended", self.name)

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
        if self.seen_mode_line:
            self.handler({
                "action":"message",
                "channel":"#test",
                "message": json.dumps(obj)})
        if obj.get("command","") == "366":
            self.seen_mode_line = True

    def end(self):
        return

class PluginLoader:
    def __init__(self, handler):
        self.handler = handler
    def end(self):
        pass
    def handleMessage(self, obj):
        if obj.get('command','') == 'PRIVMSG':
            line = obj['args'][1].split(" ", 3)
            if line[0] == "!plugin" and len(line) >= 3:
                # ['!plugin', '[un]load', 'name'] + optional code
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
            log("PluginManager End of {}", name)
            plugin = self.plugins[name]
            plugin.end()
            del self.plugins[name]

    def loadPlugin(self, name, plugin):
        log("Loading plugin {} into {}", name, self.plugins)
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
        if obj.get("action","") == "plugin":
            method = obj["method"]
            name = obj["name"]
            if method == "load":
                log("handlePluginMessage Code: {}",
                        obj['code'].replace("\\n", "\n"))
                self.loadPlugin(name,
                        CodePlugin(self.handlePluginMessage, name, (
                            "#!/usr/bin/env python\n" +
                            "import json\n" +
                            "line=json.loads(input())\n" +
                            obj["code"].replace('\\n','\n'))))
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
        #log("Plugin_output:")
        #pprint.pprint(obj)

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
    try:
        while True:
            data = sock.recv(1024)
            read += data.decode('utf-8')
            lines = read.split("\r\n")
            lines, read = lines[:-1],lines[-1]
            for line in lines:
                #import subprocess
                #subprocess.Popen("clear").wait()
                print(">> {}".format(line))
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






import pprint
import json
import threading
import subprocess

from .utils import log

class DebugPlugin:
    """ Print out the messages that plugins would receive, through stdout"""
    def __init__(self, bot):
        self.bot = bot

    def handleMessage(self, message):
        log("----DEBUG---- \n{}", pprint.pformat(message))

class ScriptStarterPlugin:
    """Delay the loading of scripts until after all the MOTD
    and channel joins and nick messages etcc.. are done.

    When you receive your first channel/pm message 'PRIVMSG'
    it's assumed you're ready.
    """

    def __init__(self, plugins):
        self.plugins = plugins

    def __call__(self, bot):
        self.bot = bot
        return self

    def handleMessage(self, message):
        if message['command'] == 'PRIVMSG':
            for plugin in self.plugins:
                self.bot.loadPlugin(ScriptPlugin(plugin))
            self.bot.unload()


class ScriptPlugin:
    """Launch a bash script as a plugin.
    bash scripts are launched as
    bash plugins/{plugin name}/start.sh
    """
    def __init__(self, script):
        self.script = script

    def __call__(self, bot):
        self.bot = bot
        self.start()
        return self

    def start(self):
        executable = ["bash", "start.sh"]
        self.running = True
        self.proc = subprocess.Popen(executable,
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            cwd="plugins/" + self.script)


        def readThread():
            print("Read thread")
            while self.running:
                line = self.proc.stdout.readline().decode('utf-8')
                if not line:
                    log(self.script +" read empty line. dieing")
                    self.die()
                    return

                try:
                    line = line.strip()
                    self.handleProcessMessage(json.loads(line))
                except:
                    print("E:" + line)
                    #self.die()
                    #log(self.script + " had an exception")
                    #raise

        self.thread = threading.Thread(target=readThread)
        self.thread.start()
        log("started {}".format(self.script))

    def handleProcessMessage(self, message):
        command = message.get("command", "")
        commands = {
                # Map of commands to (callback, [args])
                "message": (self.bot.privmsg, ["channel", "message"])
        }
        # magic.

        func,args = commands.get(command, (lambda :None, []))
        func(*map(message.get, args))


    def handleMessage(self, message):
        try:
            print("HandleMessage:", message)
            self.proc.stdin.write(json.dumps(message).encode('utf-8') + b"\n")
            self.proc.stdin.flush()
        except:
            self.bot.privmsg("#test", "Plugin: {} has died.".format(self.script))
            self.die()

    def die(self):
        self.running = False
        try:
            self.proc.terminate()
        except:
            pass
        self.bot.unload()

    def __del__(self):
        self.die()



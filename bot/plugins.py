import pprint
import json
import threading
import subprocess
import traceback

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
        self.running = False
        self.proc = None
        self.lock = threading.RLock()

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
            stderr = subprocess.PIPE,
            cwd="plugins/" + self.script)


        def reader(stream, callback):
            while self.running:
                line = stream.readline().decode('utf-8').rstrip()
                if not line:
                    self.proc.poll() # Check if we're still alive.
                    if self.proc is not None:
                        self.die()

                callback(line)

        def stdout(line):
            try:
                log("script {} out {}", self.script, line)
                if line:
                    self.handleProcessMessage(json.loads(line))
                    return
            except:
                traceback.print_exc()
            self.die()

        def stderr(line):
            log("script {} err {}", self.script, line)


        threading.Thread(target=reader, args=(self.proc.stdout, stdout)).start()
        threading.Thread(target=reader, args=(self.proc.stderr, stderr)).start()
        log("script {} start ".format(self.script))

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
            self.proc.stdin.write(json.dumps(message).encode('utf-8') + b"\n")
            self.proc.stdin.flush()
        except:
            self.bot.privmsg("#test", "Plugin: {} has died.", self.script)
            self.die()

    def die(self):
        with self.lock:
            if not self.running:
                #already dead.
                return
            self.running = False

        log("script {} end ", self.script)

        try:
            self.proc.terminate()
        except:
            pass
        self.bot.unload()

    def __del__(self):
        self.die()



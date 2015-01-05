import pprint
import json
import threading
import subprocess
import traceback

from .utils import log

class PingPlugin:
    """Respond to pings"""
    def __init__(self, bot):
        self.bot = bot

    def handleMessage(self, message):
        """ Send a PONG response to each PING command."""
        if message['command'] == 'PING':
            self.bot.quote("PONG {}", message['args'][0])

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
        self.timeout = 1
        self.lock = threading.RLock()

    def __call__(self, bot):
        self.bot = bot
        self.start()
        return self

    def start(self):
        """ Start the plugin process.
        execute bash plugins/{plugin name}/start.sh
        pipe stderr to the bots stdout
        pipe stdout to a handler
        setup a stdin for handleMessage to write to.
        """

        if self.proc:
            log("script {} killing old instance.", self.script);
            self.proc.stdin.close()
            self.proc.stdout.close()
            self.proc.stderr.close()
            self.proc.wait()
            log("script {} killed old instance.", self.script);

        executable = ["bash", "start.sh"]
        self.running = True
        self.proc = subprocess.Popen(executable,
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            cwd="plugins/" + self.script)


        def reader(stream, callback):
            """ Generic stream reading thread.
            Read a line, pass it to the callback.
            Handle end of stream """
            while self.running:
                line = stream.readline().decode('utf-8').rstrip()
                if not line:
                    self.checkAlive()
                    if not self.running:
                        return

                    callback(line)

        def stdout(line):
            """ Lines from the plugins stdout go to this wrappers
            handleProcessMessage as an object"""
            try:
                log("script {} out {}", self.script, line)
                if line:
                    self.handleProcessMessage(json.loads(line))
                    return
            except:
                traceback.print_exc()
                loc("script {} had an exception while processing '{}'", this.script, line)

        def stderr(line):
            """ Stderr is just piped to the bots stdout"""
            log("script {} err {}", self.script, line)

        threading.Thread(target=reader, args=(self.proc.stdout, stdout)).start()
        threading.Thread(target=reader, args=(self.proc.stderr, stderr)).start()
        log("script {} start ".format(self.script))

    def handleProcessMessage(self, message):
        """ Take the plugin output (dict) and produce the right
        bot.API calls """

        command = message.get("command", "")
        commands = {
                # Map of commands to (callback, [args])
                "message": (self.bot.privmsg, ["channel", "message"])
        }
        # magic.

        func,args = commands.get(command, (lambda :None, []))
        func(*map(message.get, args))


    def handleMessage(self, message):
        """ Send a message (dict) to the plugin process. """
        try:
            self.proc.stdin.write(json.dumps(message).encode('utf-8') + b"\n")
            self.proc.stdin.flush()
        except:
            self.bot.privmsg("#test", "script {} had a stdin exception", self.script)
            self.checkAlive()

    def checkAlive(self):
        """ Validate if the plugin is still alive, update self.running.
        If the process has exited with a non-zero exit code, reload the plugin.
        """
        with self.lock:
            if not self.running:
                return

            self.proc.poll()
            if self.proc.returncode is None:
                return

            self.running = False


        log("script {} exited with code {}", self.script, self.proc.returncode)

        if self.proc.returncode != 0:
            log("script {} had an error exit code. Restarting in {}s", self.script, self.timeout)
            #self.bot.load(ScriptPlugin(self.script))
            threading.Timer(self.timeout, self.start).start()    
        else:
            self.bot.unload()

    def __del__(self):
        """ The bot calls this upon plugin removal
        python /should/ call this upon shutdown.

        Attempt to kill the process"""
        with self.lock:
            if self.running:
                self.proc.terminate()
            self.proc.wait()
            self.proc.stdin.close()
            self.proc.stdout.close()
            self.proc.stderr.close()
            self.running = False

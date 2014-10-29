import json
import threading
import subprocess
def log(msg, *args):
    msg = msg.format(*args) +" "
    first, rest = msg.split(" ",1)
    print("\033[33m{}\033[0m {}".format(first, rest))



class CodePlugin:
    """ Keep a singleton select loop that runs on a map of fileno->CodePlugins
    """
    __ID = 0
    def __init__(self, handler, name, code):
        CodePlugin.__ID += 1
        log("[CodePlugin] New code plugin:\n[{}]{}", name, code)
        self.log = lambda msg,*args:log("{} " + msg, name, *args)
        self.handler = handler
        self.name = name
        self.code = code
        self.path = "/dev/shm/" + name + str(CodePlugin.__ID)
        f = open(self.path, "w")
        f.write(code)
        f.close()
        self.running = False
        self.start()

    def start(self):
        line = self.code.split("\n")[0]
        if not line.startswith("#!"):
            print("Error: code doesn't start with #!...", self.code)
            return
        line = line[2:]

        executable = line.split(" ")
        executable.append(self.path)
        self.log("running {}", executable)
        self.proc = subprocess.Popen(executable,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
            #, cwd = "/dev/shm/")

        def readThread():
            self.running = True
            while self.running:
                self.log("waiting")
                line = self.proc.stdout.readline().decode('utf-8')
                self.log("read {}", line)

                if not line:
                    self.log("Empty line, checking if we exited")
                    if self.checkExitState():
                        return

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
                # only start if the last exit was an error code
                self.start()

            #log("Sending {} to {}", obj, self.name)
            #log("Sending to {}", self.name)
            self.proc.stdin.write(json.dumps(obj).encode('utf-8') + b"\n")
            self.proc.stdin.flush()
        except:
            #self.restart()
            raise

    def checkExitState(self):
        self.proc.poll()
        if self.proc.returncode is None:
            self.log("Process hasn't exited.")
            return False
        self.log("Exit code {}", self.proc.returncode)

        # If the exit code is 0, the process exited normally,
        # this is a signal that we can reload the plugin.
        if self.proc.returncode is not 0:
            # Log the exit code
            self.handler({"action":"message",
                "channel":"#test",
                "message":"Plugin {} exited with code {}"
                        .format(self.name, self.proc.returncode)})
            # Unload the process
            self.handler({"action":"plugin",
                "method":"unload",
                "name":self.name})
        return True

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
                    code = (
                        "#!/usr/bin/env python\n" +
                        "import json\n" +
                        "line=json.loads(input())\n" +
                        obj["code"].replace('\\n','\n')
                    )

                    code += line[3]

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



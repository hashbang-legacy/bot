import subprocess
subprocess.Popen("clear").wait()
from util import thread
import select

class Plugin(object):
    def __init__(self, name, code):
        self.code = code
        self.name = name
        self.proc = None
        self.deaths = 0
        self.start()

    def needsRemoved(self):
        self.proc.poll()
        if self.proc.returncode is not None:
            print("{} has died with code {}".format(
                self.name, self.proc.returncode))

            self.deaths += 1

            if self.deaths >= 5:
                return True

            self.start()

        return False
    def start(self):
        path = "/dev/shm/" + self.name
        f = open(path, "w")
        f.write(self.code)
        f.close()
        print("started {}".format(self.name))
        self.proc = subprocess.Popen(["/usr/bin/env", "python", "-u", path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd = "/dev/shm/")

        @thread
        def foo():
            while True:
                line = self.proc.stderr.readline()
                if line:
                    print("[Err] {}: {}".format(self.name, line.decode('utf-8')[:-1]))
                else:
                    return
    def fileno(self):
        return self.proc.stdout.fileno()

    def readline(self):
        line = self.proc.stdout.readline().decode('utf-8')
        if not line:
            self.needsRemoved()

        return line

    def writeline(self, data):
        try:
            self.proc.stdin.write("{}\n".format(data).encode('utf-8'))
            self.proc.stdin.flush()
        except:
            if not self.needsRemoved():
                self.writeline(data)

import threading
plugin_lock = threading.RLock()
def pluginLock(f):
    def f2(*a, **b):
        with plugin_lock:
            return f(*a, **b)
    return f2

plugins = {}
@pluginLock
def unloadPlugin(name):
    print("PM: kill " + name)
    if name in plugins:
        plugins[name].proc.terminate()
        del plugins[name]

@pluginLock
def loadPlugin(name, code):
    unloadPlugin(name)
    print("PM: load " + name)
    plugins[name] = Plugin(name, code)

@pluginLock
def prune():
    print("Pruning")
    for key in list(plugins.keys()):
        if plugins[key].needsRemoved():
            del plugins[key]
            _toSend.append({
                'plugin':'SYSTEM',
                'value': json.dumps({
                    "target": "#test",
                    "message": "Plugin {} died 5 times.".format(key)})})

import json
@pluginLock
def process(line):
    # Check a plugins output for a plugin manager command
    # return true if we consume this line
    # return false if the line should be forwarded out of the
    #     plugin manager
    if line['value'].startswith("{"):
            obj = json.loads(line['value'])
            if obj.get("type", "") == "plugin":
                print("Plugin manager processing: {}".format(obj))
                action = obj.get("action","")
                name = obj.get("name","")
                if action == "load":
                    loadPlugin(name, obj.get("code",""))
                elif action == "unload":
                    unloadPlugin(name)
                return True
    return False


@pluginLock
def send(line):
    # Send a line to all of the plugins
    prune()
    print("Writing line to each plugin:", type(line))
    for plugin in plugins.values():
        plugin.writeline(line)

_toSend = []
def recv():
    if not _toSend:
        prune()
        plugin_list = plugins.values()
        r, w, x = select.select(plugin_list,[],[])
        for pipe in r:
            _toSend.append({
                "plugin":pipe.name,
                "value": pipe.readline()
            })
    line = _toSend.pop(0)

    if process(line):
        return {}
    return line

if __name__ == "__main__":
    loadPlugin("foo", """print(4)""")
    loadPlugin("bar", """
import time
while True:
    time.sleep(.1)
    print("Hello world")
""")
    loadPlugin("baz", """
print('bazbazbazbaz')
import time, json
while True:
    time.sleep(.2)
    print(json.dumps({
        'message':'tick',
        'channel':'#test'
    }))
    """)

    @thread
    def foo():
        import time
        time.sleep(1)
        loadPlugin("bar", """
import json
def unload(name):
    print(json.dumps({
        'type': 'plugin',
        'action': 'unload',
        'name': name
    }))
unload('baz')
unload('bar')
""")
    while True:
        print(recv())

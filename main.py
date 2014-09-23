from connect import *
import plugins
import util

password = input("hashbangbot's password:")
c = JSONIrc(connect(('localhost', 4445), '[bot]', "hashbangbot:" + password))
plugins.loadPlugin("loader", open("loader.py").read())

import json
@thread
def foo():
    while True:
        print("[Main] Reading from connection")
        line = c.recv()
        print("C->PM: {}".format(line))
        plugins.send(json.dumps(line))

while True:
    print("[Main] Reading from plugin manager")
    obj = plugins.recv()
    if obj:
        assert(type(obj) == dict)
        assert("value" in obj)
        line = obj['value']
        if line == "":
            continue
        print("PM->C: {}".format(line))
        c.send(json.loads(line))

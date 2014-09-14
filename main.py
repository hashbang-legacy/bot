from connect import *
import plugins
import util

password = input("hashbangbot's password:")
c = JSONIrc(connect(('localhost', 4445), '[bot]', "hashbangbot:" + password))


plugins.loadPlugin("loader", """
import json, sys, pprint
while True:
    try:
        line = input()
        obj = json.loads(line)
        msg = obj['message'].split(" ",3)
        pprint.pprint(msg,stream=sys.stderr)

        if msg[0] != '!plugin':
            continue

        name = msg[2]
        if msg[1] == 'load':
            print(json.dumps({
                'type':'plugin', 'action':'load', 'name':name, 'code': msg[3]
            }))
        elif msg[1] == 'unload':
            print(json.dumps({
                'type':'plugin', 'action':'unload', 'name':name
            }))
        sys.stdout.flush()
    except:
        import traceback
        traceback.print_exc()
""")
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

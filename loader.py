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
                'type':'plugin',
                'action':'load',
                'name':name,
                'code': msg[3]
            }))
        elif msg[1] == 'unload':
            print(json.dumps({
                'type':'plugin',
                'action':'unload',
                'name':name
            }))
        sys.stdout.flush()
    except:
        import traceback
        traceback.print_exc()


import json
import urllib.request

DDG = "http://duckduckgo.com/?o=json&q={}"

while True:
    obj = json.loads(input())

    if obj['command'] != 'PRIVMSG':
        continue

    # This needs to be better...
    nick = obj['prefix'].split("!")[0]
    chan = obj['args'][0]

    term = obj['args'][1]
    if term.startswith("!gs "):
        term = term[4:]
    elif term.startswith("!ddg "):
        term = term[5:]
    else:
        continue

    result = json.loads(urllib.request.urlopen(DDG.format(term)).read().decode('utf-8'))

    print(json.dumps({
        "command": "message",
        "channel": chan,
        "message": "{}: {}".format( nick, result["AbstractURL"])
    }))



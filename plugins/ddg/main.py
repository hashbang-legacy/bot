import json
import urllib.request

DDG = "http://duckduckgo.com/?o=json&q={}"

while True:
    obj = json.loads(input())['message']

    if obj['command'] != 'PRIVMSG':
        continue

    nick = obj['nick']
    chan = obj['chan']
    cmd =  obj['cmd']
    terms = obj['terms']

    if cmd not in ['!gs', '!ddg']:
        continue

    result = json.loads(
        urllib.request.urlopen(DDG.format(terms)).read().decode('utf-8')
    )

    print(json.dumps({
        "command": "message",
        "channel": chan,
        "message": "{}: {}".format( nick, result["AbstractURL"])
    }))



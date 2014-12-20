"""
Urban Dictionary definitions.
"""

import json
import urllib.request

API_URL = 'http://api.urbandictionary.com/v0/define?term={}'

while True:
    obj = json.loads(input())

    if obj['command'] != 'PRIVMSG':
        continue

    nick = obj['nick']
    chan = obj['chan']
    cmd = obj['cmd']
    terms = obj['terms']

    if cmd not in ['!ud',]:
        continue

    result = json.loads(
        urllib.request.urlopen(API_URL.format(terms)).read().decode('utf-8')
    )

    defs = result.get('list', [])

    outs = []

    # Eventually allow grabbing n result.
    if defs:
        definition = defs[0].get('definition', '')
        example = defs[0].get('example', '')

        if definition:
            outs.append(
                json.dumps({
                    "command": "message",
                    "channel": chan,
                    "message": "{}: {}".format( nick, definition)
                })
            )

        if example:
            outs.append(
                json.dumps({
                    "command": "message",
                    "channel": chan,
                    "message": "{}: {}".format( nick, example)
                })
            )

    else:
        outs.append(
            json.dumps({
                    "command": "message",
                    "channel": chan,
                    "message": "{}: {}".format( nick, "No results found :(")
            })
        )

    for out in outs:
        print(out)

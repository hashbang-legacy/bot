"""
Urban Dictionary definitions.
"""

import json
import urllib.request

API_URL = 'http://api.urbandictionary.com/v0/define?term={}'

while True:
    obj = json.loads(input())['message']

    if obj['command'] != 'PRIVMSG':
        continue

    nick = obj['nick']
    chan = obj['chan']
    cmd = obj['cmd']
    terms = obj['terms']

    if cmd not in ['!ud',]:
        continue

    split_terms = terms.split(' ')

    idx = 0

    if split_terms and len(split_terms) > 1:
        try:
            idx = int(split_terms[-1])

            split_terms.pop() # Don't want integer in call.

        except ValueError:
            pass

    # Join multipe terms for API call.
    terms = '+'.join(split_terms)

    result = json.loads(
        urllib.request.urlopen(API_URL.format(terms)).read().decode('utf-8')
    )

    defs = result.get('list', [])
    amount = len(defs)

    outs = []

    if idx > amount - 1:
        idx = amount - 1

    if defs:

        max_length = 350

        definition = defs[idx].get('definition', '')

        if len(definition) > max_length:
            definition = definition[:max_length] + '...'

        example = defs[idx].get('example', '')

        if len(example) > max_length:
            example = example[:max_length] + '...'

        if definition:
            outs.append(
                json.dumps({
                    "command": "message",
                    "channel": chan,
                    "message": "{}: <Definition [{} of {}]>: {}".format(nick, idx + 1, amount, definition)
                })
            )

        if example:
            outs.append(
                json.dumps({
                    "command": "message",
                    "channel": chan,
                    "message": "{}: <Example>: {}".format(nick, example)
                })
            )

    else:
        outs.append(
            json.dumps({
                    "command": "message",
                    "channel": chan,
                    "message": "{}: {}".format(nick, "No results found :(")
            })
        )

    for out in outs:
        print(out)

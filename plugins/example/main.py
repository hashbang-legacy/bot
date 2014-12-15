import json
color = "\0034"
nocolor = "\0030"
kv_str = "\"\0033{}\0030\":{}"

while True:
    line = input()
    message = json.loads(line)

    if message['command'] == 'PING':
        # Pings are noisy, skip them
        continue

    # Format a nice string
    out = ", ".join([
        kv_str.format(key, json.dumps(value))
        for (key, value) in sorted(message.items())
    ])

    print(json.dumps({
        "command": "message",
        "channel": "#test",
        "message": "{{" + out + "}}"
        }))

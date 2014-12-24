import json
while True:
    event = json.loads(input())['message']
    if event["command"] != "PRIVMSG" or event["cmd"] != "!repeat":
        continue

    print(json.dumps({
        "command": "message",
        "channel": event["chan"],
        "message": event["terms"]
        }))

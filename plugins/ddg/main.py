import json
import urllib.request

DDG = "http://duckduckgo.com/?o=json&q={}"

# Read a json object from stdin
obj = json.loads(input())

# Check that it's !gs or !ddg
if obj.get('cmd', '') in ['!gs', '!ddg']: 
    
    # Read the search results
    url = DDG.format(obj['terms'])
    response = urllib.request.urlopen(url).read().decode('utf-8')
    result = json.loads(response)["AbstractURL"]

    # Send the response
    nick = obj['nick']
    chan = obj['chan']
    print(json.dumps({
        "command": "message",
        "channel": chan,
        "message": "{}: {}".format(nick, result)
    }))

# exit normally

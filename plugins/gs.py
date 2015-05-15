import api
import urllib.request
import urllib.parse
import json
_API_URL = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q="

@api.onCommand("gs")
def search(who, what, where):
    reply_json = urllib.request.urlopen(_API_URL + urllib.parse.quote(what)).read()
    response = json.loads(reply_json.decode("utf-8"))
    data = response['responseData']
    if "results" not in data or len(data['results']) == 0:
        api.privmsg(where, "No results :(")
        return

    result = data['results'][0]
    reply = "<{C3}Google Search{}: {B}%s{} | {LINK}%s{} >" % (
            result['titleNoFormatting'],
            urllib.parse.unquote(result['url']))
    api.privmsg(where, reply)

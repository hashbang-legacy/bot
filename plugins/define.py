import api
import re
import urllib.request
import json

url = "https://glosbe.com/gapi/translate?from=eng&dest=eng&format=json&page=1&phrase="
cache = {}

def define(phrase):
    data = urllib.request.urlopen(url + phrase).read().decode("utf-8")
    jdata = json.loads(data)
    if "tuc" not in jdata:
      return []
    return jdata[0]["meanings"]

@api.onCommand("gd")
#@api.onCommand("define")
def handle(who, msg, where):
    res = re.match("^([0-9]+ |)(.*)$", msg)
    if not res:
        return
    num, term = res.groups()
    if not term:
      return api.privmsg(where, usage)

    if num:
        num = int(num.strip())
    else:
        num = 1

    if num < 1:
        num = 1

    val = cache.get(term, None)
    if val is None:
        val = define(term)
        cache[term]=val

    n = len(val)
    if n == 0:
        api.privmsg(where, noDefinitions.format(term=term))
        return
    num -= 1
    if num >= n:
        api.privmsg(where, invalidArg.format(term = term, tot = n))
        return

    definition = val[num]["text"]
    api.privmsg(where, definitionFmt.format(
      num = num + 1,
      tot = n,
      term = term,
      definition = definition))

usage = "!gd [num] TERM"
noDefinitions = "No definition for '{term}' found."
invalidArg = "{term}  has {tot} definitions. [1-{tot}]"
definitionFmt = "<{{C3}}Definition{{}} {{B}}{num}{{}} (of {tot}) for {{B}}{term}{{}}> {definition}"

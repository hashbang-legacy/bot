import api
import html
import json
import re
import urllib.parse
import urllib.request

url_re = "(https?[^\\s]+)"


def getTitle(url):
    try:
        data = urllib.request.urlopen(url).read().decode("utf-8")
        title = " ".join(data.split("<title>")[1].split("</title>")[0].split())
        return html.unescape(title)[:100]
    except:
        return ""
def shorten(url):
    safeurl = urllib.parse.quote(url)
    v_gd = "http://v.gd/create.php?format=simple&url="
    resp = urllib.request.urlopen(v_gd + safeurl).read()
    return resp.decode('utf-8')


@api.onPrivmsg()
def handle(who, msg, where):
  parts = re.split(url_re, msg, 1) # Only grab the first url. lame i know.
  if len(parts) == 1:
    return

  url = parts[1]

  short = ""
  if len(url) >= 20: # Long enough for a shorten
    short = shorten(url)
    short = shortFmt.format(shorten(url))

  title = getTitle(url)
  if title:
    title = titleFmt.format(title)

  if short or title:
    divider = ""
    if short and title:
      divider = delim
    out = outputFmt.format(short=short, delim=divider, title=title)
    api.privmsg(where, out)

delim = " | "
shortFmt = "{{LINK}}{}{{}}"
titleFmt = "{{blue}}Title{{}}: {{yellow}}{}{{}}"
outputFmt = "<{short}{delim}{title}>"


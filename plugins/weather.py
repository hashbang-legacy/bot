import api
import urllib.request
import urllib.parse
import json

def getWeather(location):
    # yql's gross. perhaps i can find something cleaner. wunderground wasn't bad
    # duplicated from
    # https://github.com/hashbang/irc-bot/blob/master/plugins/weather.lua
    location = location.replace("'", "\\'")

    query = "select * from weather.forecast where woeid in (" +\
            "select woeid from geo.places(1) where text='" +\
            location +\
            "') and u='f'"

    url = "http://query.yahooapis.com/v1/public/yql?q=" +\
        urllib.parse.quote(query) + "&format=json"

    resp = urllib.request.urlopen(url).read().decode('utf-8')
    result = json.loads(resp)['query']
    item = result['results']['channel']['item']

    temp = int(item['condition']['temp'])

    # Build the output, add some color to it.
    out = [
        item['title'].replace("for ", "for {yellow}").replace(" at ", "{} at "),
        "{blue}" + item['condition']['text'] + "{}",
        "{}°F".format(temp),
        "({} °C)".format((temp - 32)*5//9)]

    return " ".join(out)


@api.onCommand("w")
def doWeather(who, msg, where):
    res = getWeather(msg)

    api.privmsg(where, res)

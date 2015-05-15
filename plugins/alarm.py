import api
import datetime
import parsedatetime
import db
import threading
parse = parsedatetime.Calendar().parse

store = db.Shelve({
    "next":[]
})
cache = store["next"]

def cron():
    threading.Timer(1, cron).start()
    now = datetime.datetime.now()
    if len(cache) == 0:
        return
    changed = False

    while len(cache) > 0:
        if now >= cache[0][0]:
            changed= True
            when, where, what = cache.pop(0)
            api.privmsg(where, what)
        else:
            break

    if changed:
        store["next"] = cache
cron()

def schedule(when, where, what):
    cache.append((when, where, what))
    cache.sort()
    store["next"] = cache



#@api.usage(usage) # todo figure out how to make usage work
@api.onCommand("alarm")
def printDate(sender, args, replyTo):
  if '>' not in args:
    # print usage and leave.
    return api.privmsg(replyTo, "Bad usage")
  timeSpec, note = args.split(">",1)

  msg = "({}) {}: {}".format(
    datetime.datetime.now().strftime("%x %X"),
    sender,
    note)
  when = datetime.datetime(*parse(timeSpec)[0][:6])
  schedule(when, replyTo, msg)



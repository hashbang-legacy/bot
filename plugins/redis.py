import api
import db
import shlex

redis = db.Redis(db=1)
whitelist=[
    k
    for k in dir(redis)
    if not (
      k.startswith("_") or
      k[0].isupper()
      )]
print(whitelist)
@api.onCommand("redis")
def cmd(who, args, chan):
  args = shlex.split(args)

  cmd = args[0]
  if cmd not in whitelist:
    api.msg(chan, errFmt.format("Invalid command"))
    return

  try:
    ret = getattr(redis, cmd)(*args[1:])
  except db.redis.exceptions.ResponseError as e:
    api.msg(chan, errFmt.format(e))
    return

  api.msg(chan, okFmt.format(ret))

okFmt = "[{{GREEN}}Redis{{}}]:{!r}"
errFmt = "[{{RED}}Redis{{}}]:{!r}"


"""
Various database providers, as well as some wrapers and backing logic over them.

"""
import util.caller
import shelve
import sqlite3
import redis
# Gets overwritten during testing
def shelve_opener(filename):
  return shelve.open("data/" + filename)

def Shelve(default = {}):
  filename = util.caller.getCaller()+".shlv"
  db = shelve_opener(filename)

  for k,v in default.items():
    if k not in db:
      db[k]=v
  return db

# Gets overwritten during testing
def sqlite3_opener(db):
  return sqlite3.connect("data/" + db)

def Sqlite3(defaultCommands=[]):
  filename = util.caller.getCaller()+".sql3"
  db = sqlite3_opener(filename)
  c = db.cursor()
  for instr in defaultCommands:
    c.execute(instr)
  db.commit()
  return db

def redis_opener(host, port, db):
    return redis.StrictRedis(host=host, port=port, db=db)

def Redis(host="localhost", port=6379, db=0):
    cli = redis_opener(host, port, db)
    # Seeding ?
    return cli

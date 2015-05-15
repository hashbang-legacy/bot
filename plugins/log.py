import api
import db
import time

store = db.Sqlite3([
    """CREATE TABLE IF NOT EXISTS raw(time int, line text)""",
    """CREATE TABLE IF NOT EXISTS messages(time integer, line TEXT, src text, dst TEXT)"""
])
c = store.cursor()

@api.onPrivmsg()
def message(who, what, where):
    c.execute("INSERT INTO messages values (?, ?, ?, ?)", (
        int(time.time()), what, who, where))
    store.commit()
    print("Logged message")

@api.onRawLine()
def raw(line):
    if line.startswith("PING"):
        return

    c.execute("INSERT INTO raw values (?, ?)", (
        int(time.time()), line))
    store.commit()
    print("Logged raw")



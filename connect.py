import socket
import multiprocessing
from util import *

DEBUG = False
def connect(hostport, nick, password):
    """ Setup an irc connection
        Returns a connection that you can:
            send(str)
            recv() -> str
        Trailing \r\n are automatically added for send,
        and are not returned in recv()

        Pings are automatically handled.
    """
    sock = socket.socket()
    sock.connect(hostport)
    def send(message, *args):
        data = (message + "\r\n").format(*args).encode('utf-8')
        sock.send(data)

        if DEBUG:
            print("[{}] SEND {}".format(nick, data))

    # Handshake
    if password:
        send("PASS {}", password)
    send("NICK {}", nick)
    send("USER a b c d :e")

    # IO pipes
    local,remote = multiprocessing.Pipe()
    @thread
    def netToPipe():
        read = ""
        while True:
            data = sock.recv(1024)
            read += data.decode('utf-8')
            lines = read.split("\r\n")
            lines, read = lines[:-1],lines[-1]
            for line in lines:
                if line.startswith("PING"):
                    remote.send("PONG" + line[4:]) # Respond to pong

                if DEBUG:
                    print("[{}] RECV {}".format(nick, line))

                local.send(line)
    @thread
    def pipeToNet():
        while True:
            send(local.recv())

    return remote



class Pipe:
    def send(self, msg):
        pass
    def recv(self):
        pass

def parsemsg(s):
    """Breaks a message from an IRC server into its prefix, command, and arguments.
    Taken from twisted irc.
    """
    prefix = ''
    trailing = []
    if not s:
       raise IRCBadMessage("Empty line.")
    if s[0] == ':':
        prefix, s = s[1:].split(' ', 1)
    if s.find(' :') != -1:
        s, trailing = s.split(' :', 1)
        args = s.split()
        args.append(trailing)
    else:
        args = s.split()
    command = args.pop(0)
    return prefix, command, args

class JSONIrc(Pipe):
    def __init__(self, connection):
        self.connection = connection

    def send(self, obj):
        assert(type(obj) == dict)
        print("Trying to send: {} to irc".format(obj))
        # send a json object
        to = obj['target']
        msg = obj['message']
        self.connection.send("PRIVMSG {} :{}".format(to, msg))

    def recv(self):
        while True:
            line = self.connection.recv()
            prefix, cmd, args = parsemsg(line)
            if cmd == 'PRIVMSG':
                return {
                    "target": args[0],
                    "message": args[1],
                    "sender": prefix.split("!")[0],
                    "raw": line
                }
            else:
                print("E:{}".format(line))

if __name__ == "__main__":
    c = JSONIrc(connect(('localhost', 4445), '[bot]', 'hashbangbot:password'))
    c.send({'target':'#test', 'message': 'autorepeat plugin turned on'})
    while True:
        c.send(c.recv())



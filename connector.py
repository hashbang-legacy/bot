#!/usr/bin/env python3
import socket, ssl, select, os, threading, configparser, time

class SocketBase:
    def __init__(self):
        self.sock = None

    def connect(self):
        pass

    def send(self, text):
        try:
            print(self.name,"<<",text.strip()[:60])
            text = text.encode('utf-8')
            self.sock.send(text)
            return
        except Exception as e:
          pass
        print(self.name, "(Missed)")

    def read(self):
        if self.sock is None:
            print("[%s Connecting]" % self.name)
            self.connect()
            print("[%s Connected]" % self.name)

        try:
            ret = self.sock.recv(1024).decode('utf-8', 'ignore')

            if ret == "":
                self.sock = None
                return self.read()

            print(self.name,">>",ret.strip()[:60])
            return ret
        except Exception as e:
            print(e)
            self.sock = None
            raise # This should go away
        return self.read()


class IrcSocket(SocketBase):
    name = "Irc"
    def connect(self):
        host, port = "irc.hashbang.sh", 6697
        nick = "`"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if connection.get("ssl", False):
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = True
            context.load_default_certs()
            s = context.wrap_socket(s, server_hostname=host)

        connected = False
        delay = 1
        while not connected:
            try:
                s.connect((connection["host"],
                    int(connection.get("port", "6667"))))
                connected = True
            except Exception:
                print("[Connection refused]")
                print("Waiting {}s".format(delay))
                time.sleep(delay)
                delay *= 2
                if delay > 30:
                    delay = 30

        self.sock = s

        self.send("USER {} {} * :{}\r\n".format(
            registration["username"],
            registration["mode"],
            registration["realname"]
            ))

        self.send("NICK {}\r\n".format(
            registration["nick"]
            ))
        self.autorun = True

class LocalSocket(SocketBase):
    name = "Local"
    def __init__(self, sockfile):
      super().__init__()
      self.sock_file = sockfile
      self.name = "Local"
      self.sock = None
      #try:
      #    os.unlink(LocalSocket.sock_file)
      #except:pass
      self.localSock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
      self.localSock.bind(self.sock_file)
      self.localSock.listen(1)


    def connect(self):
      self.sock,_ = self.localSock.accept()

def serverToLocal():
    buff = ""
    while True:
        read = irc.read()
        buff += read
        while "\n" in buff:
            line, buff = buff.split("\n",1)
            if line.startswith("PING "):
                irc.send(line.replace("PING", "PONG")+"\n")
                if irc.autorun:
                    irc.autorun = False
                    i = 1
                    while str(i) in autorun:
                        line = autorun[str(i)]
                        irc.send(line + "\r\n")
                        i += 1


        local.send(read)

def localToServer():
    while True:
        irc.send(local.read())


os.system("clear")

conf = configparser.ConfigParser()
conf.read("config.cfg")
connection = conf["Connection"] # Required
registration = conf["Registration"] # Required
autorun = conf["Autorun"] if "Autorun" in conf else {} # Optional

local = LocalSocket(connection["local"])
local.connect() # Wait for a connection locally before trying to connect remotely
irc = IrcSocket()

a = threading.Thread(target=serverToLocal)
b = threading.Thread(target=localToServer)
a.start()
b.start()

a.join()
b.join()


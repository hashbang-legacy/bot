#!/usr/bin/env python3
import socket, ssl, select, os, threading, configparser, time

class IrcClient:
  def __init__(self, toBot):
    self.loadConfig()
    self.connect()
    self.sendToBot = toBot
    threading.Thread(target=self.loop).start()

  def loadConfig(self):
    # Read the config file.
    conf = configparser.ConfigParser()
    conf.read("config.cfg")
    self.connection = conf["Connection"] # Required
    self.registration = conf["Registration"] # Required
    self.autorun = conf["Autorun"] if "Autorun" in conf else {} # Optional

  def getSocket(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if self.connection.get("ssl", False):
      context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
      context.verify_mode = ssl.CERT_REQUIRED
      context.check_hostname = True
      context.load_default_certs()
      s = context.wrap_socket(s, server_hostname=self.connection["host"])
    return s

  def send(self, text):
    self.sock.send(text.encode('utf-8'))
    self.sock.send(b'\r\n')

  def connect(self):
    self.sock = self.getSocket()
    try:
      self.sock.connect((
        self.connection["host"],
        int(self.connection.get("port", "6667"))))
    except:
      print("Connection failed.")
      time.sleep(5)
      exit(0)

    self.send("USER {} {} * :{}\r\n".format(
        self.registration["username"],
        self.registration["mode"],
        self.registration["realname"]
        ))

    self.send("NICK {}\r\n".format(
        self.registration["nick"]
        ))

  def loop(self):
    autorun = False

    f = self.sock.makefile()
    while True:
      line = f.readline().strip()
      if not line:
        print("EOF")
        exit(1)
      print("Read:", line)
      if line.startswith("PING"):
        self.send(line.replace("PING", "PONG"))

        if not autorun:
          autorun = True
          i = 1
          while str(i) in self.autorun:
            line = self.autorun[str(i)]
            self.send(line)
            i += 1
      self.sendToBot(line)

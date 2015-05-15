#!/usr/bin/env python3
import configparser
conf = configparser.ConfigParser()
conf.read("config.cfg")
sock_file = conf.get("Connection", "local")

from util.color import parse_colors
from api import handlers
import os

import socket, sys, threading


class socks:
  local = None

def sendline(line):
  if socks.local is None:
    shutdown()
  else:
    line = parse_colors(line) + "\r\n"
    socks.local.send(line.encode("utf-8"))

def readLocal():
    handlers.register("sendline", sendline)
    for f in os.listdir("plugins"):
        if not f.endswith(".py"): # Not python? skip.
          continue
        if f.endswith("test.py"): # Python, but is a test? skip.
          continue
        name = f.split(".")[0]
        __import__("plugins." + name)


    data = ""
    socks.local.settimeout(.1)
    while True:
        try:
            read = socks.local.recv(1024).decode('utf-8')
        except socket.timeout:
            continue
        print(">>", read)
        if read == '':
            print("[remote disconnect]")
            shutdown()
            return

        data += read
        while "\n" in data:
            line, data = data.split("\n", 1)
            try:
                handleLine(line.replace("\r",""))
            except Exception as e:
                import traceback
                traceback.print_exc()


def mainLoop():
  #handlers.emitEvent("ready")
  while True:
    try:
        line = sys.stdin.readline()
    except KeyboardInterrupt:
        print("Keyboard interrupt. closing socket")
        socks.local.close()
        return
    socks.local.send(line.encode('utf-8'))

def shutdown():
  pass

def handleLine(line):
  handlers.emitEvent("line", line)

socks.local = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
socks.local.connect(sock_file)
b = threading.Thread(target=readLocal)
b.start()
mainLoop()
b.join()

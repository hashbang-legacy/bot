#!/usr/bin/env python3
from util.color import parse_colors
from api import handlers
import os

def loadPlugins():
  for f in os.listdir("plugins"):
    if not f.endswith(".py"): # Not python? skip.
      continue
    if f.endswith("test.py"): # Python, but is a test? skip.
      continue

    name = f.split(".")[0]
    __import__("plugins." + name)

def mainLoop(pipe):
  def sendline(line):
    print("<<BOT<<", line)
    pipe.send(parse_colors(line))

  handlers.register("sendline", sendline)
  loadPlugins()
  while True:
    line = pipe.recv()
    print(">>BOT>>", line)
    handlers.emitEvent("line", line)

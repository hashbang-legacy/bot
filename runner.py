from threading import Thread
import select
from multiprocessing import Pipe, Queue
import multiprocessing

class Plugin:
  def __init__(self, name, onMessage):
    self.running = False
    self.local_pipe, self.remote_pipe = Pipe()
    self.name = name
    self.onMessage = onMessage
    self.start()

  def start(self):
    assert not self.running, "Already running."
    self.running = True
    self.thread = Thread(target=self.run)
    self.thread.start()
    Thread(target=self.reader).start()

  def reader(self):
    while self.running:
      print("Checking for plugin output")
      r, _, _ = select.select([self.local_pipe],[],[],.5)
      print(r)
      if r:
        print("Available!")
        got = self.local_pipe.recv()
        print("Read:", got)
        self.onMessage(got)

  def restart(self):
    self.proc.terminate()

  def stop(self):
    assert self.running, "Running"
    self.running = False
    self.remote_pipe.close()
    self.local_pipe.close()
    self.proc.terminate()
    self.thread.join()

  def run(self):
    while self.running:
      print("Staring %s" % self.name)
      self.proc = multiprocessing.Process(
          target=__pluginLauncher__,
          args=(self.remote_pipe, self.name))
      self.proc.start()
      self.proc.join()
      print("Exited %s" % self.name)

  def send(self, line):
    self.local_pipe.send(line)




def __pluginLauncher__(pipe, pluginName):
  import setproctitle
  setproctitle.setproctitle("plugin_" + pluginName)

  import api
  module = __import__("plugins." + pluginName)
  api.register("sendline", pipe.send)
  while True:
    line = pipe.recv()
    print("Remote read:" + line)
    api.emitEvent("line", line)

def __ircLauncher__(pipe):
  import connector
  client = connector.IrcClient(pipe.send)
  while True:
      client.send(pipe.recv())


class Bot:
  def __init__(self):
    self.toIrc = Queue()
    self.irc = Process("IRC", __ircLauncher__)
    self.plugins = {}

  def loop(self):
    ircPipe = self.irc.getPipe()
    while True:
      ircPipe.send(self.toIrc.get())

  def pluginReader(self, pipe):
    while True:
      self.toIrc.put(pipe.recv())

  def startPlugin(self, plugin):
    plugin = Process("Plugin:%s" % plugin, __pluginLauncher__, plugin)
    pipe = plugin.getPipe()
    self.plugins[pipe] = plugin
    Thread(target=self.pluginReader, args=(pipe,)).start()

if __name__=="__main__":
  def handler(line):
    print(line)
  p = Plugin("db_example", handler)
  import time
  time.sleep(2)
  p.send(":nick!user@host PRIVMSG #chan :!loads")
  time.sleep(1)
  p.restart()
  time.sleep(1)
  p.send(":nick!user@host PRIVMSG #chan :!loads")
  time.sleep(1)
  import os
  os.system("killall plugin_db_example")
  time.sleep(1)
  p.send(":nick!user@host PRIVMSG #chan :!loads")
  time.sleep(1)
  p.stop()
  time.sleep(1)
  #  p.send(":nick!user@host PRIVMSG #chan :!loads")
  #  time.sleep(1)

  #b = Bot()
  #b.startPlugin("repeat")
  #try:
  #  b.loop()
  #except KeyboardInterrupt:
  #  print("Keyboard interrupt. abandon ship")
  #  exit(0)

from threading import Thread
from multiprocessing import Pipe, Queue
import multiprocessing
class Process:
  def __init__(self, name, target, *args):
    self.running = False
    self.local, self.remote = Pipe()
    self.name = name
    self.args = (self.remote,) + args
    self.target = target
    self.start()

  def getPipe(self):
    return self.local

  def start(self):
    assert not self.running, "Already running."
    self.running = True
    self.thread = Thread(target=self.run)
    self.thread.start()

  def restart(self):
    self.proc.terminate()

  def stop(self):
    assert self.running, "Running"
    self.running = False
    self.proc.terminate()
    self.thread.join()
    self.remote_pipe.close()
    self.local_pipe.close()

  def run(self):
    while self.running:
      print("Staring %s" % self.name)
      self.proc = multiprocessing.Process(
          target=self.target, args=self.args)
      self.proc.start()
      self.proc.join()
      print("Exited %s" % self.name)

def __pluginLauncher__(pipe, pluginName):
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
  b = Bot()
  b.startPlugin("repeat")
  try:
    b.loop()
  except KeyboardInterrupt:
    print("Keyboard interrupt. abandon ship")
    exit(0)

from multiprocessing import Process, Pipe
from threading import Thread

# Plugin process side main entry point.
def launch(pluginName, pipe):
  import api
  module = __import__("plugins." + pluginName)
  api.register("sendline", pipe.send)
  while True:
    line = pipe.recv()
    print("Remote read:" + line)
    api.emitEvent("line", line)


# Main process side plugin wrapper
class PluginRunner:
  def __init__(self, plugin):
    self.name = plugin
    self.proc = None
    self.running = False
    self.local_pipe, self.remote_pipe = Pipe()

  def getConnection(self):
    return self.local_pipe

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
      self.proc = Process(target=launch, args=('repeat', self.remote_pipe))
      self.proc.start()
      print("Waiting on proc to end")
      self.proc.join()

# Main process example.
if __name__=="__main__":

  plugin = PluginRunner("repeat")
  pipe = plugin.getConnection()

  def reader():
    try:
      while True:
        print("Main read:" + pipe.recv())
    except:
      print("Main reader ended.")
  Thread(target = reader).start()

  plugin.start()
  import time
  time.sleep(1)
  plugin.restart()

  pipe.send(":Nick!user@host PRIVMSG #chan :!repeat test")
  time.sleep(.1)
  plugin.stop()

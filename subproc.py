
print("subproc imported")

def mainLoop(pipe):
  line = pipe.recv()
  print("subproc got", line)
  pipe.send(line + "...")

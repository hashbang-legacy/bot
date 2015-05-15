__handlers = {
  "line": [],
  "sendline": []
}

def unregister(event, callback):
  __handlers[event].remove(callback)

def register(event, callback):
  __handlers[event].append(callback)

def emitEvent(event, *args):
  for handler in __handlers.get(event, []):
    handler(*args)


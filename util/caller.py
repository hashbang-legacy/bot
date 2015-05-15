import inspect
import os
def getCaller():
  return os.path.basename(inspect.stack()[2][1])[:-3]

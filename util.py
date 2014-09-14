import threading
import multiprocessing
def thread(func):
    """ Convenience decorator/method for running functions in another thread"""
    def helper():
        try:
            func()
        except:
            import traceback
            traceback.print_exc()

    threading.Thread(target=helper).start()
    return func

def pipeCloser(pipe):
    _recv = pipe.recv
    _close = pipe.close

    def recv():
        val = _recv()
        if val is None:
            raise IOError("Connection closed")
        return val

    def close():
        pipe.send(None)
        _close()
    pipe.recv = recv
    pipe.close = close
    return pipe

def Pipe():
    return map(pipeCloser, multiprocessing.Pipe())



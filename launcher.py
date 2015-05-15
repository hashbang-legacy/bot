#from http.server import BaseHTTPRequestHandler, HTTPServer
#import json
#
#port = 8075 # BOTS
#class Handler(BaseHTTPRequestHandler):
#    def do_POST(self):
#        obj = json.loads(self.rfile.read().decode('utf-8', 'ignore'))
#        import pprint
#        pprint.pprint(obj)
#
#server = HTTPServer(('', port), Handler)
#server.serve_forever()

from multiprocessing import Process, Pipe
import threading, time
import signal

def runBody(queue):
    import bot
    bot.mainLoop(queue)

def keepBodyAlive(state, pipe):
    while state["running"]:
        print("keeyBodyAlive")
        p = Process(target=runBody, args=(child,))
        state["proc"] = p
        p.start()
        p.join()
        time.sleep(5)
    print("keepBodyAlive exits")

if __name__ == "__main__":
    state = {"running": True, "proc": None}
    pipe, child = Pipe()

    def onsignal(signal, frame):
        print("Caught signal", state)
        state["running"] = False
        pipe.close()
        child.close()
        state["proc"].terminate()
    signal.signal(signal.SIGINT, onsignal)


    threading.Thread(target=keepBodyAlive,
            args=(state, child)).start()

    import connector
    connector.mainLoop(pipe, state)

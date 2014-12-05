""" Various IRC / Bot utility functions. """

def parsemsg(line):
    """
    Breaks a message from an IRC server into its prefix, command, and
    arguments. Returns a dict with those (as well as 'raw' for original text)
    Taken from twisted irc.
    """

    prefix = ''
    trailing = []
    if not line:
        return {}
    s = line
    if s[0] == ':':
        prefix, s = s[1:].split(' ', 1)
    if s.find(' :') != -1:
        s, trailing = s.split(' :', 1)
        args = s.split()
        args.append(trailing)
    else:
        args = s.split()
    command = args.pop(0)
    return {'prefix':prefix, 'command':command, 'args':args, 'raw':line}


def log(msg, *args):
    """
    Colored logging.
    """
    msg = msg.format(*args) +" "
    first, rest = msg.split(" ",1)
    print("\033[33m{}\033[0m {}".format(first, rest))

def connect(config):
    import socket
    sock = socket.socket()
    sock.connect((config['host'], config['port']))
    return sock

def messageIterator(socket):
    read = ""
    try:
        while True:
            data = socket.recv(1024)
            if not data:
                return

            read += data.decode('utf-8')
            lines = read.split("\r\n")
            lines, read = lines[:-1],lines[-1]

            for line in lines:
                yield parsemsg(line)

    except KeyboardInterrupt:
        log("Keyboard interrupt")
        return



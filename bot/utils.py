""" Various IRC / Bot utility functions. """
import re

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

    msg = {
       'prefix' : prefix,
       'command': command,
       'args'   : args,
       'raw'    :  line
    }

    return annotatemsg(msg)

def annotatemsg(msg):
    """
    Depending on command type will add useful properties to msg object.
    """

    command = msg['command']

    if command == 'PRIVMSG':
        args = msg['args']
        nick = msg['prefix'].split('!')[0]
        chan = args[0]
        parts = args[1].split(' ')

        msg.update({
            'nick'  : nick,
            'chan'  : chan,
            'cmd'   : parts[0],
            'terms' : ' '.join(parts[1:]).strip(),
        })

    return msg

def log(msg, *args):
    """
    Colored logging.
    """
    msg = msg.format(*args) +" "
    first, rest = msg.split(" ",1)
    print("\033[33m{}\033[0m {}".format(first, rest))

class RecordedSock:
    def __init__(self, sock, filename):
        self.sock = sock
        if filename == "-":
            import sys
            self.stream = sys.stdout
        else:
            self.stream = open(filename, "w")

    def send(self, message):
        print("<" + message.decode('utf-8').encode('unicode_escape').decode('ascii'), file = self.stream)
        self.sock.send(message)

    def recv(self, count):
        message = self.sock.recv(count)
        print(">" + message.decode('utf-8').encode('unicode_escape').decode('ascii'), file = self.stream)
        return message

    def __del__(self):
        self.stream.flush()

def connect(config):
    """ Connect to
    config['host'] on port config['port'] (default 6667)

    if config["RecordNetData"] has been set, record network data to that file.
    """

    import socket
    sock = socket.socket()
    sock.connect((config['host'], config.get('port', 6667))) # Default port 6667

    if config.get("RecordNetData", ""):
        sock = RecordedSock(sock, config.get("RecordNetData"));

    return sock

def messageIterator(socket):
    """ Given a socket, read data from it and yield each complete message
    This removes the trailing \r\n.
    """
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

def colorize(format_string):
    """
    Colorize a message formatted with color markers.
    Color markers take the form of 
    {white} or {red} (see colorize_text for specifics).
    """
    parts = re.split("\{([^\}]*)\}", format_string)

    colored_parts = [parts[0]]
    
    colors = parts[1::2]
    strings= parts[2::2]

    for (color, text) in zip(colors, strings):
        colored_parts.append(
                colorize_text(
                    text, *color.split(",")[:2]))
    
    return "".join(colored_parts)

def colorize_text(text, fg='white', bg='black'):
    """
    Human friendly k/v mapping of IRC colors.

    @fg : Text color
    @bg : Background color
    """

    mapping = {
       'white'       : '00',
       'black'       : '01',
       'blue'        : '02',
       'green'       : '03',
       'red'         : '04',
       'brown'       : '05',
       'purple'      : '06',
       'orange'      : '07',
       'yellow'      : '08',
       'light_green' : '09',
       'teal'        : '10',
       'light_cyan'  : '11',
       'light_blue'  : '12',
       'pink'        : '13',
       'grey'        : '14',
       'light_grey'  : '15'
    }

    color_format = '\x03{},{}{}\x03'

    if not fg in mapping:
        fg = 'white'

    if not bg in mapping:
        bg = 'black'

    return color_format.format(
        mapping[fg],
        mapping[bg],
        text
    )

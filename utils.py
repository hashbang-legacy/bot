def log(msg, *args):
    msg = msg.format(*args) +" "
    first, rest = msg.split(" ",1)
    print("\033[33m{}\033[0m {}".format(first, rest))


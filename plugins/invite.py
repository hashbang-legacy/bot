import api

@api.onInvite()
def invited(sender, chan):
    if chan.startswith("#"):
        api.join(chan)


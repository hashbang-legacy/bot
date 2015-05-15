import api
@api.onCommand("donate")
def donateLine(sender, msg, to):
  api.privmsg(to, "[{C8}Bitcoin {C11}1DtTvCLiUMhs21QcETQzLyiqxoopUjqBSU{}][{C8}Wallet {C11}donate@hashbang.sh{}][{C8}PayPal {C11}http://goo.gl/aSQWy0{}]")


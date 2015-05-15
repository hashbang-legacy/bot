import api
import time
import subprocess

version = subprocess.check_output(["git", "show", "-s", "--format=%h"]).decode('utf-8', 'ignore').strip()

@api.onCTCP("VERSION")
def onVersion(who, cmd, args):
  api.ctcp(who,"VERSION", "scaling-octo-robot " + version)

@api.onCTCP("TIME")
def onTime(who, cmd, args):
  api.ctcp(who, "TIME", time.ctime())

import os
import sys
import urllib2
import json
import time

from mylog import logger
log = logger.log

from btsx import BTSX

from config import read_config
from market_speculator import MarketSpeculator

if len(sys.argv) < 2:
    print "Usage:  main.py config_path"
    sys.exit(1)

conf = read_config(sys.argv[1])

print conf

client = BTSX(
    conf["client"]["rpc_user"],
    conf["client"]["rpc_password"],
    conf["client"]["rpc_port"]
)

feeds = []


bots = []
for botconfig in conf["bots"]:
    if botconfig["bot_type"] == "market_speculator":
        bots.append(MarketSpeculator(client, feeds, botconfig))
    else:
        raise Exception("unknown bot type")


while True:
    for bot in bots:
        bot.execute()
    time.sleep(10)

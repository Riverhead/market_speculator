import time
from mylog import logger
log = logger.log


# This bot provides liquidity and maintains the peg

class MarketSpeculator():
    def __init__(self, client, feeds, bot_config):
        self.client = client
        if not "bot_type" in bot_config or bot_config["bot_type"] != "market_speculator":
            raise Exception("Bad bot configuration object")
        self.config = bot_config
        self.name = self.config["account_name"]
        self.base_symbol = bot_config["asset_pair"][0]
        self.quote_symbol = bot_config["asset_pair"][1]

    def execute(self):
        SPREAD = self.config["spread_percent"]
        tolerance = self.config["spread_tolerance"]
        sec_since_update = 0
        last_price = self.client.get_last_fill(self.base_symbol, self.quote_symbol)
        start_btsx = float(self.client.get_balance(self.name, self.quote_symbol))

        btsx_balance = self.client.get_balance(self.name, self.quote_symbol)
        usd_balance = self.client.get_balance(self.name, self.base_symbol)
        last_ask    = last_price
        last_bid    = last_price

        while True:

            new_price = self.client.get_last_fill(self.base_symbol, self.quote_symbol)

            usd_balance = self.client.get_balance(self.name, self.base_symbol)
            btsx_balance = self.client.get_balance(self.name, self.quote_symbol)

            if usd_balance > 10:
               self.client.submit_bid(self.name, 0.3*(usd_balance / last_ask), self.quote_symbol, last_ask * (1-SPREAD), self.base_symbol)
               last_bid = last_ask * (1-SPREAD)
               sec_since_update = 0
            if btsx_balance > 500:
               self.client.submit_ask(self.name, 0.3*btsx_balance, self.quote_symbol, last_bid * (1+SPREAD), self.base_symbol)
               last_ask = last_bid * (1+SPREAD)
               sec_since_update = 0

            print ("Seconds since last action: %i USD %f BTSX %f started %f" % (sec_since_update, usd_balance, btsx_balance, start_btsx))

            time.sleep(2)
            sec_since_update += 2

            if (abs(new_price - last_price) / last_price) > ( tolerance ):
               log("Price moved -  old:  %f   new:  %f" % (last_price, new_price))
                  
               sec_since_update = 0
    
               self.client.cancel_all_orders(self.name, self.base_symbol, self.quote_symbol)
               self.client.wait_for_block()

               last_price = new_price
               last_ask    = last_price
               last_bid    = last_price



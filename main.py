import time
import json
from sys import path
path.append('../')
from keys import *

# Import Exchange Clients
from binance.client import Client as binanceClient
from kucoin.client import Client as kucoinClient
from bittrex.bittrex import Bittrex as bittrexClient, API_V2_0


# Twilio Dependencies
from sendsms import *
from twilio.rest import Client as twilioClient

# initiate Clients
binanceclient = binanceClient(binance_key(), binance_secret())
kucoinclient = kucoinClient(kucoin_key(), kucoin_secret())
bittrexclient = bittrexClient(bittrex_key(), bittrex_secret(), api_version=API_V2_0)
twilioclient = twilioClient(twilio_account_sid(), twilio_auth_token())

print "checking trading pairs..."
new_exchange_symbols = {}

# get exchange api returns for tickers TODO add exchange class with abstracted get_pairs(), get_name(), etc. methods
binance_trading_symbols = binanceclient.get_all_tickers()
kucoin_trading_symbols = kucoinclient.get_trading_symbols()
bittrex_currencies = bittrexclient.get_currencies()[u'result']

# encode pairs/symbols to lists
new_exchange_symbols['binance'] = [price['symbol'].encode('utf-8') for price in binance_trading_symbols]
new_exchange_symbols['kucoin'] = [dicts[u'symbol'].encode('utf-8') for dicts in kucoin_trading_symbols]
new_exchange_symbols['bittrex'] = [dicts[u'Currency'].encode('utf-8') for dicts in bittrex_currencies]

# Load recent exchange symbols as dict
old_exchange_symbols = {}
with open('recentexchangesymbols.json', 'r') as f:
    old_exchange_symbols = json.load(f)

for exchange in new_exchange_symbols.keys():
    new_listings = []
    for symbol in new_exchange_symbols[exchange]:
        if symbol not in old_exchange_symbols[exchange]:
            old_exchange_symbols[exchange].append(symbol)
            new_listings.append(symbol)

    # Send text if new listing
    if len(new_listings) > 0:
        print "New Trading Pairs on " + exchange + "!: ", new_listings
        numbers = ["+16174606842", "+15748499823", "+13363911192"]
        for number in numbers:
            try:
                message = twilioclient.messages.create(
                  to=number,
                  from_= twilio_from_number(),
                  body="New " + exchange + " listing: " + str(new_listings))
                print "SMS sent. MID: ", message.sid
            except Exception as e:
                pass

with open('recentexchangesymbols.json', 'w') as f:
    f.write(json.dumps(old_exchange_symbols, indent=4))

## JSON schema for recentexchangesymbols.json
# {
#   "binance" : [],
#   "kucoin" : [],
#   "bittex" : []
# }

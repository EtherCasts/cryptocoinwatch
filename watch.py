#!/usr/bin/env python

import requests
import sys

from utils import address_to_hex

DEFAULT_ADDRESS = "36PrZ1KHYMpqSyAQXSG8VwbUiq2EogxLo2"

def getreceivedbyaddress(address, confirmations=6):
    url = "https://blockchain.info/q/getreceivedbyaddress/%s?confirmations=%d" % (address, confirmations)
    r = requests.get(url)
    if r.status_code == 200:
        return int(r.text)
    print "ERROR", r.status_code, r.text

def watch(address):
    hex_value = address_to_hex(address)
    value = getreceivedbyaddress(address)
    print address, hex_value, value

if __name__ == '__main__':
    if len(sys.argv) > 1:
        address = sys.argv[1]
    else:
        address = DEFAULT_ADDRESS
    watch(address)

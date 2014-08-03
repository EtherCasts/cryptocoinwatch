#!/usr/bin/env python

import argparse
import logging
import os
from pprint import pprint
import requests

from serpent import compile

import api

CONTRACT_FILE = "cryptocoinwatch.se"
ETH_JSONRPC_URI = os.getenv("ETH_JSONRPC_URI", "http://127.0.0.1:8080")

logging.disable(logging.INFO)

def getreceivedbyaddress(address, confirmations=6):
    url = "https://blockchain.info/q/getreceivedbyaddress/%s?confirmations=%d" % (address, confirmations)
    r = requests.get(url)
    if r.status_code == 200:
        return int(r.text)
    print "ERROR", r.status_code, r.text

def create(api):
    contract = compile(open('cryptocoinwatch.se').read()).encode('hex')
    contract_address = api.create(contract)
    print "Contract is available at %s" % contract_address
    api.wait_for_next_block(verbose=True)

def status(api):
    print "Coinbase: %s" % api.coinbase()
    print "Listening? %s" % api.is_listening()
    print "Mining? %s" % api.is_mining()
    print "Peer count: %d" % api.peer_count()

    last_block = api.last_block()
    print "Last Block:"
    pprint(last_block)

    keys = api.keys()
    print "Keys:"
    for key in keys:
        address = api.secret_to_address(key)
        balance = api.balance_at(address)
        print "- %s %.4e" % (address, balance)

def transact(api, dest, value=10 ** 18):
    api.transact(dest, value=value)
    api.wait_for_next_block(verbose=True)

def poll(api, contract_address):
    if not api.is_contract_at(contract_address):
        print "No contract found at %s" % contract_address
        return

    watch_list = api.storage_at(contract_address, "0x20")
    print "WATCH_LIST", watch_list

    # hex_value = address_to_hex(address)
    # value = getreceivedbyaddress(address)
    # print address, hex_value, value

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--create', action='store_true', help="create the contract")
    parser.add_argument('--poll', help="poll the contract state")
    parser.add_argument('--status', action='store_true', help="display the eth node status")
    parser.add_argument('--transact', help="transact 1 ETH to destination")
    args = parser.parse_args()

    eth_api = api.Api(ETH_JSONRPC_URI)

    if args.create:
        create(eth_api)
    elif args.poll:
        poll(eth_api, args.poll)
    elif args.status:
        status(eth_api)
    elif args.transact:
        transact(eth_api, args.transact)
    else:
        parser.print_usage()

if __name__ == '__main__':
    main()

#!/usr/bin/env python

import argparse
import logging
import os
from pprint import pprint
import requests
import time

from serpent import compile

import api
from utils import address_to_hex, hex_to_address, xhex, xint

CONTRACT_FILE = "contracts/cryptocoinwatch.se"
ETH_JSONRPC_URI = os.getenv("ETH_JSONRPC_URI", "http://127.0.0.1:8080")

ADDRESS_OFFSET = 2 ** 160
ADDRESS_RECORD_SIZE = 4

UPDATE_INTERVAL = 3600

logging.disable(logging.INFO)

def getreceivedbyaddress(address, confirmations=6):
    url = "https://blockchain.info/q/getreceivedbyaddress/%s?confirmations=%d" % (address, confirmations)
    r = requests.get(url)
    if r.status_code == 200:
        return int(r.text)
    print "ERROR", r.status_code, r.text

def get_address_record(api, contract, address):
    res = api.call(contract, funid=4, data=[address])
    received_by_address, last_updated, nr_watched, last_watched = res
    return {
        'received_by_address': received_by_address,
        'last_updated': last_updated,
        'nr_watched': nr_watched,
        'last_watched': last_watched}

def cmd_create(args):
    contract = compile(open(CONTRACT_FILE).read()).encode('hex')
    contract_address = args.api.create(contract)
    print "Contract is available at %s" % contract_address
    if args.wait:
        args.api.wait_for_next_block(verbose=True)

def cmd_getreceivedbyaddress(args):
    hex_value = address_to_hex(args.address)
    record = get_address_record(args.api, args.contract_address, xint(hex_value))
    pprint(record)

def cmd_status(args):
    print "Coinbase: %s" % args.api.coinbase()
    print "Listening? %s" % args.api.is_listening()
    print "Mining? %s" % args.api.is_mining()
    print "Peer count: %d" % args.api.peer_count()
    print "Number: %d" % args.api.number()

    last_block = args.api.last_block()
    print "Last Block:"
    pprint(last_block)

    accounts = args.api.accounts()
    print "Accounts:"
    for address in accounts:
        balance = args.api.balance_at(address)
        print "- %s %.4e" % (address, balance)

def cmd_transact(args):
    args.api.transact(args.dest, value=args.value * 10 ** 18)
    if args.wait:
        args.api.wait_for_next_block(verbose=True)

def update_address(api, contract_address, hex_value):
    address = hex_to_address(hex_value)
    print "ADDRESS", address

    record = get_address_record(api, contract_address, xint(hex_value))
    epoch_time = int(time.time())

    if epoch_time - record['last_updated'] > UPDATE_INTERVAL:
        value = getreceivedbyaddress(address)
        print "VALUE", value
        api.transact(contract_address, funid=6, data=[xint(hex_value), value])
        print "updated"
    else:
        print "not updating, already recently updated"

def cmd_poll(args):
    coinbase = args.api.coinbase()
    if not coinbase:
        print "No coinbase found"
        return

    if not args.api.is_contract_at(args.contract_address):
        print "No contract found at %s" % args.contract_address
        return

    owner = args.api.state_at(args.contract_address, "0x")
    print "OWNER", owner
    if owner != coinbase:
        print "You are not the owner of the contract"
        return

    watch_list = args.api.state_at(args.contract_address, "0x04")
    print "WATCH_LIST", watch_list

    if watch_list != '0x':
        for idx in range(int(watch_list, 16)):
            hex_value = args.api.state_at(args.contract_address, xhex(0x04 + idx + 1))
            update_address(args.api, args.contract_address, hex_value)

def cmd_watch(args):
    hex_value = address_to_hex(args.address)

    print "Watching", hex_value

    args.api.transact(args.contract_address, funid=3, data=[xint(hex_value)])
    if args.wait:
        args.api.wait_for_next_block(verbose=True)

def main():
    parser = argparse.ArgumentParser()
    parser.set_defaults(api=api.Api(ETH_JSONRPC_URI))

    subparsers = parser.add_subparsers(help='sub-command help')
    parser_create = subparsers.add_parser('create', help='create the contract')
    parser_create.set_defaults(func=cmd_create)
    parser_create.add_argument('--wait', action='store_true', help='wait for block to be mined')

    parser_getreceivedbyaddress = subparsers.add_parser('getreceivedbyaddress', help='getreceivedbyaddress')
    parser_getreceivedbyaddress.set_defaults(func=cmd_getreceivedbyaddress)
    parser_getreceivedbyaddress.add_argument('contract_address', help='contract address')
    parser_getreceivedbyaddress.add_argument('address', help='cryptocurrency address')

    parser_poll = subparsers.add_parser('poll', help='poll the contract state')
    parser_poll.set_defaults(func=cmd_poll)
    parser_poll.add_argument('contract_address', help='contract address')

    parser_status = subparsers.add_parser('status', help='display the eth node status')
    parser_status.set_defaults(func=cmd_status)

    parser_transact = subparsers.add_parser('transact', help='transact ether to destination (default: 1 ETH)')
    parser_transact.set_defaults(func=cmd_transact)
    parser_transact.add_argument('dest', help='destination')
    parser_transact.add_argument('--value', type=int, default=1, help='value to transfer in ether')
    parser_transact.add_argument('--wait', action='store_true', help='wait for block to be mined')

    parser_watch = subparsers.add_parser('watch', help='watch the address')
    parser_watch.set_defaults(func=cmd_watch)
    parser_watch.add_argument('contract_address', help='contract address')
    parser_watch.add_argument('address', help='cryptocurrency address')
    parser_watch.add_argument('--wait', action='store_true', help='wait for block to be mined')

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()

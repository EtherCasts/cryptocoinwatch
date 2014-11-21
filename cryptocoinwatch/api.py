import json
import requests
import sys
import time
from uuid import uuid4

from pyethereum import utils
import serpent

JSONRPC_URL = "http://127.0.0.1:8080"

DEFAULT_GAS = 10000
GAS_PRICE = 10 * 10 ** 12

DEFAULT_KEY = '0x' + utils.sha3("cow").encode('hex')  # part of the Genesis block
DEFAULT_ADDRESS = '0x' + utils.privtoaddr(DEFAULT_KEY[2:])  # cd2a3d9f938e13cd947ec05abc7fe734df8dd826
# FIXME using cow address doesn't work
DEFAULT_ADDRESS = '0x8928602aaee4d7cec275e0da580805f6949cfe98'


class ApiException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return "code=%d, message=\"%s\"" % (self.code, self.message)


class Api(object):

    def __init__(self, jsonrpc_url=JSONRPC_URL):
        self.jsonrpc_url = jsonrpc_url

    def _rpc_post(self, method, params):
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid4()),
            "method": method,
            "params": params}
        headers = {'content-type': 'application/json'}

        r = requests.post(self.jsonrpc_url, data=json.dumps(payload), headers=headers)
        if r.status_code >= 400:
            raise ApiException(r.status_code, r.reason)

        response = r.json()

        if 'error' in response:
            raise ApiException(response['error']['code'], response['error']['message'])

        return response.get('result')

    def accounts(self):
        return self._rpc_post('eth_accounts', None)

    def balance_at(self, address):
        params = [address]
        balance = self._rpc_post('eth_balanceAt', params)
        if balance == "0x":
            return 0
        else:
            return int(balance, 16)

    def block(self, nr):
        params = [nr]
        return self._rpc_post('eth_blockByNumber', params)

    def check(self, addresses):
        params = {
            'a': addresses
        }
        return self._rpc_post('check', params)

    def coinbase(self):
        return self._rpc_post('eth_coinbase', None)

    def create(self, code, from_=DEFAULT_ADDRESS, gas=DEFAULT_GAS, gas_price=GAS_PRICE, value=0):
        if not code.startswith('0x'):
            code = '0x' + code
        params = [{'code': code}]
        # FIXME
        # params = [{
        #    'code': code,
        #    'from': from_,
        #    'gas': hex(gas),
        #    'gasPrice': hex(gas_price),
        #    'value': hex(value)}]
        return self._rpc_post('eth_transact', params)

    def is_contract_at(self, address):
        params = [address]
        return int(self._rpc_post('eth_codeAt', params), 16) != 0

    def is_listening(self):
        return self._rpc_post('eth_listening', None)

    def is_mining(self):
        return self._rpc_post('eth_mining', None)

    def key(self):
        return self._rpc_post('key', None)

    def keys(self):
        return self._rpc_post('keys', None)

    def last_block(self):
        return self.block(-1)

    def lll(self, contract):
        params = {
            's': contract
        }
        return self._rpc_post('eth_lll', params)

    def number(self):
        return self._rpc_post('eth_number', None)

    def peer_count(self):
        return self._rpc_post('eth_peerCount', None)

    def state_at(self, address, index):
        params = [address, index]
        return self._rpc_post('eth_stateAt', params)

    def storage_at(self, address):
        params = [address]
        return self._rpc_post('eth_storageAt', params)

    def transact(self, dest, from_=DEFAULT_ADDRESS, funid=None, data="", gas=DEFAULT_GAS, gas_price=GAS_PRICE, value=0):
        if not dest.startswith('0x'):
            dest = '0x' + dest

        if funid is not None:
            data = "0x" + serpent.encode_abi(funid, data).encode('hex')

        params = [{
            'to': dest,
            'data': data,
            'from': from_,
            'gas': hex(gas),
            'gasPrice': hex(gas_price),
            'value': hex(value)}]
        return self._rpc_post('eth_transact', params)

    def wait_for_next_block(self, verbose=False):
        if verbose:
            sys.stdout.write('Waiting for next block to be mined')
            start_time = time.time()

        last_block = self.last_block()
        while True:
            if verbose:
                sys.stdout.write('.')
                sys.stdout.flush()
            time.sleep(5)
            block = self.last_block()
            if block != last_block:
                break

        if verbose:
            print
            delta = time.time() - start_time
            print "Ready! Mining took %ds" % delta

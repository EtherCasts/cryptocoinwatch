from pyethereum import tester
import pyethereum.processblock as pb

from cryptocoinwatch.utils import address_to_hex, xhex

import logging
from pprint import pprint

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger()
pblogger = pb.pblogger

# customize VM log output to your needs
# hint: use 'py.test' with the '-s' option to dump logs to the console
pblogger.log_pre_state = False    # dump storage at account before execution
pblogger.log_post_state = False   # dump storage at account after execution
pblogger.log_block = False       # dump block after TX was applied
pblogger.log_memory = False      # dump memory before each op
pblogger.log_op = False           # log op, gas, stack before each op
pblogger.log_json = False        # generate machine readable output
pblogger.log_apply_op = False     # generate machine readable output
pblogger.log_stack = False        # generate machine readable output


class TestCryptoCoinWatch(object):
    ADDRESS = int(address_to_hex("36PrZ1KHYMpqSyAQXSG8VwbUiq2EogxLo2"), 16)
    ADDRESS_OFFSET = 2 ** 160
    ADDRESS_RECORD_SIZE = 4

    CONTRACT = 'contracts/cryptocoinwatch.se'

    def setup_method(self, method):
        self.s = tester.state()
        self.c = self.s.contract(self.CONTRACT)

    def _storage(self, idx):
        return self.s.block.account_to_dict(self.c)['storage'].get(idx)

    def _address_record(self, address):
        address_idx = self.ADDRESS_OFFSET + address * self.ADDRESS_RECORD_SIZE

        return {
            'received_by_address': int(self._storage(address_idx) or '0x0', 16),
            'last_updated': int(self._storage(address_idx + 1) or '0x0', 16),
            'nr_watched': int(self._storage(address_idx + 2) or '0x0', 16),
            'last_watched': int(self._storage(address_idx + 3) or '0x0', 16)}

    def test_init(self):
        assert self._storage('0x') == '0x' + tester.a0
        assert self._storage('0x01') == '0x' + 'blockchain.info'.encode('hex')
        assert self._storage('0x02') == '0x06'
        o1 = self.s.send(tester.k0, self.c, 0, funid=0, abi=[])
        assert o1 == [int('0x' + tester.a0, 16), int('0x' + 'blockchain.info'.encode('hex'), 16), 6]

    def test_echo(self):
        assert [4] == self.s.send(tester.k0, self.c, 0, funid=1, abi=[2])

    def test_suicide(self):
        o1 = self.s.send(tester.k0, self.c, 0, funid=2, abi=[])
        assert o1 == []
        assert self.s.block.get_code(self.c) == ''

    def test_suicide_by_non_owner_should_fail(self):
        o1 = self.s.send(tester.k1, self.c, 0, funid=2, abi=[])
        assert o1 == [0]
        assert self.s.block.get_code(self.c) != ''

    def test_watch(self):
        o1 = self.s.send(tester.k0, self.c, 0, funid=3, abi=[self.ADDRESS])
        assert o1 == [1]

        assert self._storage('0x04') == '0x01'  # nr_contracts
        assert self._storage('0x05') == xhex(self.ADDRESS)

        o1 = self.s.send(tester.k0, self.c, 0, funid=4, abi=[self.ADDRESS])
        assert o1 == [0, 0, 0, self.s.block.timestamp]

    def test_watch_invalid_address_should_fail(self):
        o1 = self.s.send(tester.k0, self.c, 0, ['watch', 2 ** 180])
        assert o1 == [0]

        # assert self.s.block.account_to_dict(self.c)['storage'] == {}

    def test_watch_twice_should_update(self):
        o1 = self.s.send(tester.k0, self.c, 0, ['watch', self.ADDRESS])
        assert o1 == [1]

        o2 = self.s.send(tester.k0, self.c, 0, ['watch', self.ADDRESS])
        assert o2 == [2]
        assert self._storage(0x20) == '0x01'

        assert self._address_record(self.ADDRESS) == {
            'received_by_address': 0,
            'last_updated': 0,
            'nr_watched': 2,
            'last_watched': self.s.block.timestamp}

    def test_set_get(self):
        o1 = self.s.send(tester.k0, self.c, 0, ['setreceivedbyaddress', self.ADDRESS, 255])
        assert o1 == [1]
        pprint(self.s.block.account_to_dict(self.c))
        assert self._address_record(self.ADDRESS) == {
            'received_by_address': 255,
            'last_updated': self.s.block.timestamp,
            'nr_watched': 0,
            'last_watched': 0}

        o1 = self.s.send(tester.k0, self.c, 0, ['getreceivedbyaddress', self.ADDRESS])
        assert o1 == [255, self.s.block.timestamp]

    def test_set_by_non_owner_should_fail(self):
        o1 = self.s.send(tester.k1, self.c, 0, ['setreceivedbyaddress', self.ADDRESS, 255])
        assert o1 == [0]
        assert self._storage(self.ADDRESS) is None

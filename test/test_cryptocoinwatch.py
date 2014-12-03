from pyethereum import tester
import pyethereum.processblock as pb

from cryptocoinwatch.utils import address_to_hex, xhex

import logging

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
    BLOCKCHAININFO = '0x626c6f636b636861696e2e696e666f0000000000000000000000000000000000'

    CONTRACT = 'contracts/cryptocoinwatch.se'

    FUN_GETINFO = 0
    FUN_ECHO = 1
    FUN_SUICIDE = 2
    FUN_WATCH = 3
    FUN_GETADDRESS = 4
    FUN_GETRECEIVEDBYADDRESS = 5
    FUN_SETRECEIVEDBYADDRESS = 6

    def setup_method(self, method):
        self.s = tester.state()
        self.c = self.s.contract(self.CONTRACT)

    def _storage(self, idx):
        return self.s.block.account_to_dict(self.c)['storage'].get(idx)

    def test_init(self):
        assert self._storage('0x') == '0x' + tester.a0
        assert self._storage('0x01') == self.BLOCKCHAININFO
        assert self._storage('0x02') == '0x06'

        o1 = self.s.send(tester.k0, self.c, 0, funid=self.FUN_GETINFO, abi=[])
        assert o1 == [int('0x' + tester.a0, 16), int(self.BLOCKCHAININFO, 16), 6, self.s.block.timestamp]

    def test_echo(self):
        assert [42] == self.s.send(tester.k0, self.c, 0, funid=self.FUN_ECHO, abi=[42])

    def test_suicide(self):
        o1 = self.s.send(tester.k0, self.c, 0, funid=self.FUN_SUICIDE, abi=[])
        assert o1 == []
        assert self.s.block.get_code(self.c) == ''

    def test_suicide_by_non_owner_should_fail(self):
        o1 = self.s.send(tester.k1, self.c, 0, funid=self.FUN_SUICIDE, abi=[])
        assert o1 == [0]
        assert self.s.block.get_code(self.c) != ''

    def test_watch(self):
        o1 = self.s.send(tester.k0, self.c, 0, funid=self.FUN_WATCH, abi=[self.ADDRESS])
        assert o1 == [1]

        assert self._storage('0x04') == '0x01'  # nr_contracts
        assert self._storage('0x05') == xhex(self.ADDRESS)

        o2 = self.s.send(tester.k0, self.c, 0, funid=4, abi=[self.ADDRESS])
        assert o2 == [0, 0, 1, self.s.block.timestamp]

    def test_watch_invalid_address_should_fail(self):
        o1 = self.s.send(tester.k0, self.c, 0, funid=self.FUN_WATCH, abi=[2 ** 180])
        assert o1 == [0]

    def test_watch_twice_should_update(self):
        o1 = self.s.send(tester.k0, self.c, 0, funid=self.FUN_WATCH, abi=[self.ADDRESS])
        assert o1 == [1]

        o2 = self.s.send(tester.k0, self.c, 0, funid=self.FUN_WATCH, abi=[self.ADDRESS])
        assert o2 == [2]
        assert self._storage('0x04') == '0x01'  # nr_contracts

        o3 = self.s.send(tester.k0, self.c, 0, funid=self.FUN_GETADDRESS, abi=[self.ADDRESS])
        assert o3 == [0, 0, 2, self.s.block.timestamp]

    def test_set_get(self):
        o1 = self.s.send(tester.k0, self.c, 0, funid=self.FUN_SETRECEIVEDBYADDRESS, abi=[self.ADDRESS, 255])
        assert o1 == [1]

        o2 = self.s.send(tester.k0, self.c, 0, funid=self.FUN_GETADDRESS, abi=[self.ADDRESS])
        assert o2 == [255, self.s.block.timestamp, 0, 0]

        o3 = self.s.send(tester.k0, self.c, 0, funid=self.FUN_GETRECEIVEDBYADDRESS, abi=[self.ADDRESS])
        assert o3 == [255, self.s.block.timestamp]

    def test_set_by_non_owner_should_fail(self):
        o1 = self.s.send(tester.k1, self.c, 0, funid=self.FUN_SETRECEIVEDBYADDRESS, abi=[self.ADDRESS, 255])
        assert o1 == [0]

        o2 = self.s.send(tester.k0, self.c, 0, funid=self.FUN_GETADDRESS, abi=[self.ADDRESS])
        assert o2 == [0, 0, 0, 0]

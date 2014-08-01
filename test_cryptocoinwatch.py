from pyethereum import tester

import logging
from pprint import pprint

def hex_pad(x):
    return "{0:#0{1}x}".format(x, 66)

def xhex(x):
    return "{0:#x}".format(x)


class TestCryptoCoinWatch(object):
    ADDRESS = 0x3399bc19f2b20473d417e31472c92947b59f95f8  # base58check_to_hex 36PrZ1KHYMpqSyAQXSG8VwbUiq2EogxLo2
    ADDRESS_OFFSET = 2 ** 160
    ADDRESS_RECORD_SIZE = 4

    @classmethod
    def setup_class(cls):
        logging.disable(logging.INFO)  # disable DEBUG logging of pyethereum.processblock
        cls.code = open('cryptocoinwatch.se').read()

    def setup_method(self, method):
        self.s = tester.state()
        self.c = self.s.contract(self.code)

    def _storage(self, idx):
        idx = hex_pad(idx)
        return self.s.block.account_to_dict(self.c)['storage'].get(idx)

    def _address_record(self, address):
        address_idx = self.ADDRESS_OFFSET + address * self.ADDRESS_RECORD_SIZE

        return {
            'received_by_address': int(self._storage(address_idx) or '0x0', 16),
            'last_updated': int(self._storage(address_idx + 1) or '0x0', 16),
            'nr_watched': int(self._storage(address_idx + 2) or '0x0', 16),
            'last_watched': int(self._storage(address_idx + 3) or '0x0', 16)}

    def test_init(self):
        assert self._storage(0x10) == '0x' + tester.a0
        assert self._storage(0x11) == '0x' + 'blockchain.info'.encode('hex')
        assert self._storage(0x12) == '0x06'

    def test_suicide(self):
        o1 = self.s.send(tester.k0, self.c, 0, ['suicide'])
        assert o1 == []
        assert self.s.block.get_code(self.c) == ''

    def test_suicide_by_non_owner_should_fail(self):
        o1 = self.s.send(tester.k1, self.c, 0, ['suicide'])
        assert o1 == [0]
        assert self.s.block.get_code(self.c) != ''

    def test_watch(self):
        o1 = self.s.send(tester.k0, self.c, 0, ['watch', self.ADDRESS])
        assert o1 == [1]

        assert self._storage(0x20) == '0x01'
        assert self._storage(0x21) == xhex(self.ADDRESS)

        assert self._address_record(self.ADDRESS) == {
            'received_by_address': 0,
            'last_updated': 0,
            'nr_watched': 1,
            'last_watched': self.s.block.timestamp}

    def test_watch_invalid_address_should_fail(self):
        o1 = self.s.send(tester.k0, self.c, 0, ['watch', 2 ** 180])
        assert o1 == [0]

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

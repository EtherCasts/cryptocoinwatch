from pyethereum import processblock, tester

from utils import address_to_hex, hex_pad, xhex

processblock.enable_debug()


class TestExampleBtcTrade(object):
    BTC_ADDRESS = int(address_to_hex("36PrZ1KHYMpqSyAQXSG8VwbUiq2EogxLo2"), 16)
    SELLER = int(tester.a1, 16)

    @classmethod
    def setup_class(cls):
        cls.watch_code = open('contracts/cryptocoinwatch.se').read()
        cls.trade_code = open('contracts/example_btc_trade.se').read()

    def setup_method(self, method):
        self.s = tester.state()
        print "XXX Watch contract"
        self.watch_contract = self.s.contract(self.watch_code)

        self.s.mine()

        print "XXX Trade contract"
        self.trade_contract = self.s.contract(self.trade_code)

    def _storage(self, idx):
        idx = hex_pad(idx)
        return self.s.block.account_to_dict(self.trade_contract)['storage'].get(idx)

    def test_init(self):
        assert self.watch_contract == 'c305c901078781c232a2a521c2af7980f8385ee9'
        assert self.trade_contract == 'd6f084ee15e38c4f7e091f8dd0fe6fe4a0e203ef'
        assert self._storage(0x10) == '0x' + tester.a0
        assert self._storage(0x30) == '0x01'

    def test_watch_feed(self):
        o1 = self.s.send(tester.k0, self.watch_contract, 0, ['watch', self.BTC_ADDRESS])
        assert o1 == [1]

    def test_new(self):
        now = self.s.block.timestamp
        expiry = now + 86400
        o1 = self.s.send(tester.k0, self.trade_contract, 20000,
                         ['new', self.SELLER, int(self.watch_contract, 16), self.BTC_ADDRESS, 10, expiry])
        assert o1 == [2]

        assert self._storage(0x20) == '0x01'
        assert self._storage(0x21) == xhex(self.ADDRESS)

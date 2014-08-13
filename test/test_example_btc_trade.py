from pyethereum import tester

import logging

from cryptocoinwatch.utils import address_to_hex, hex_pad, xhex

# from pyethereum import processblock
# processblock.enable_debug()


class TestExampleBtcTrade(object):
    SELLER = int(tester.a1, 16)

    BTC_ADDRESS = int(address_to_hex("36PrZ1KHYMpqSyAQXSG8VwbUiq2EogxLo2"), 16)
    BTC_AMOUNT = 100000  # in satoshi
    ETH_AMOUNT = 2 * 10 ** 18  # in wei

    @classmethod
    def setup_class(cls):
        logging.disable(logging.INFO)  # disable DEBUG logging of pyethereum.processblock
        cls.watch_code = open('contracts/cryptocoinwatch.se').read()
        cls.trade_code = open('contracts/example_btc_trade.se').read()

    def setup_method(self, method):
        self.s = tester.state()
        self.watch_contract = self.s.contract(self.watch_code)
        self.trade_contract = self.s.contract(self.trade_code)

    def _storage(self, idx):
        idx = hex_pad(idx)
        return self.s.block.account_to_dict(self.trade_contract)['storage'].get(idx)

    def test_init(self):
        assert self._storage(0x10) == '0x' + tester.a0  # buyer
        assert self._storage(0x30) == '0x01'  # state = new

    def test_watch_feed(self):
        o1 = self.s.send(tester.k0, self.watch_contract, 0, ['watch', self.BTC_ADDRESS])
        assert o1 == [1]

    def test_new(self):
        buyer_balance = self.s.block.get_balance(tester.a0)

        expiry = self.s.block.timestamp + 86400
        o1 = self.s.send(tester.k0, self.trade_contract, self.ETH_AMOUNT,
                         ['new', self.SELLER, int(self.watch_contract, 16), self.BTC_ADDRESS, self.BTC_AMOUNT, expiry])
        assert o1 == [2]  # pending

        assert self._storage(0x10) == '0x' + tester.a0  # buyer
        assert self._storage(0x11) == '0x' + tester.a1  # seller
        assert self._storage(0x12) == '0x' + self.watch_contract
        assert self._storage(0x20) == xhex(self.BTC_ADDRESS)
        assert self._storage(0x21) == xhex(self.BTC_AMOUNT)
        assert self._storage(0x22) == xhex(expiry)
        assert self._storage(0x30) == '0x02'  # state = pending

        # amount escrowed
        assert self.s.block.get_balance(self.trade_contract) == self.ETH_AMOUNT
        assert self.s.block.get_balance(tester.a0) == buyer_balance - self.ETH_AMOUNT

    def test_finish_still_pending_should_do_nothing(self):
        buyer_balance = self.s.block.get_balance(tester.a0)
        seller_balance = self.s.block.get_balance(tester.a1)

        expiry = self.s.block.timestamp + 86400
        o1 = self.s.send(tester.k0, self.trade_contract, self.ETH_AMOUNT,
                         ['new', self.SELLER, int(self.watch_contract, 16), self.BTC_ADDRESS, self.BTC_AMOUNT, expiry])
        assert o1 == [2]  # pending

        o2 = self.s.send(tester.k0, self.trade_contract, 0, ['finish'])
        assert o2 == [2]  # still pending

        # amount escrowed
        assert self.s.block.get_balance(self.trade_contract) == self.ETH_AMOUNT
        assert self.s.block.get_balance(tester.a0) == buyer_balance - self.ETH_AMOUNT
        assert self.s.block.get_balance(tester.a1) == seller_balance

    def test_finish_when_finished_should_pay_seller(self):
        buyer_balance = self.s.block.get_balance(tester.a0)
        seller_balance = self.s.block.get_balance(tester.a1)

        expiry = self.s.block.timestamp + 86400
        o1 = self.s.send(tester.k0, self.trade_contract, self.ETH_AMOUNT,
                         ['new', self.SELLER, int(self.watch_contract, 16), self.BTC_ADDRESS, self.BTC_AMOUNT, expiry])
        assert o1 == [2]  # pending

        # update datafeed
        o2 = self.s.send(tester.k0, self.watch_contract, 0, ['setreceivedbyaddress', self.BTC_ADDRESS, self.BTC_AMOUNT])
        assert o2 == [1]

        o3 = self.s.send(tester.k0, self.trade_contract, 0, ['finish'])
        assert o3 == [3]  # finished

        # seller is paid
        assert self.s.block.get_balance(self.trade_contract) == 0
        assert self.s.block.get_balance(tester.a0) == buyer_balance - self.ETH_AMOUNT
        assert self.s.block.get_balance(tester.a1) == seller_balance + self.ETH_AMOUNT

    def test_finish_while_expired_should_refund_buyer(self):
        buyer_balance = self.s.block.get_balance(tester.a0)
        seller_balance = self.s.block.get_balance(tester.a1)

        expiry = self.s.block.timestamp + 86400
        o1 = self.s.send(tester.k0, self.trade_contract, self.ETH_AMOUNT,
                         ['new', self.SELLER, int(self.watch_contract, 16), self.BTC_ADDRESS, self.BTC_AMOUNT, expiry])
        assert o1 == [2]  # pending

        assert self.s.block.get_balance(self.trade_contract) == self.ETH_AMOUNT
        assert self.s.block.get_balance(tester.a0) == buyer_balance - self.ETH_AMOUNT
        assert self.s.block.get_balance(tester.a1) == seller_balance

        # move the time forward past expiry
        self.s.block.timestamp = expiry + 1
        o2 = self.s.send(tester.k0, self.trade_contract, 0, ['finish'])
        assert o2 == [4]  # expired

        # buyer is refunded
        assert self.s.block.get_balance(self.trade_contract) == 0
        assert self.s.block.get_balance(tester.a0) == buyer_balance
        assert self.s.block.get_balance(tester.a1) == seller_balance

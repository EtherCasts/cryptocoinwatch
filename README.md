CryptoCoinWatch
===============

Ethereum datafeed to watch the amount received of crypto currencies. This data can be subsequently used by CFDs, escrows, betting contracts, etc.

## Contract

The contract `cryptocoinwatch.se` allows 3rd parties to request the datafeed to watch the `getreceivedbyaddress` value of a Bitcoin (or other altcoin) address.

When providing an address, it should be converted to the [Base58Check](https://en.bitcoin.it/wiki/Base58Check_encoding) format and prefixed with the version byte. So for the Bitcoin multisig address `36PrZ1KHYMpqSyAQXSG8VwbUiq2EogxLo2` the address to use is `0x053399bc19f2b20473d417e31472c92947b59f95f8`

This conversion can be done with [pybtctool](https://github.com/vbuterin/pybitcointools):
```
$ pybtctool b58check_to_hex 36PrZ1KHYMpqSyAQXSG8VwbUiq2EogxLo2
3399bc19f2b20473d417e31472c92947b59f95f8
$ pybtctool get_version_byte 36PrZ1KHYMpqSyAQXSG8VwbUiq2EogxLo2
5
```

The contract storage can be expected to get some metadata, there are not (yet) exposed via an API:

- `0x10` - Contract owner
- `0x11` - Data source (ie "blockchain.info")
- `0x12` - Minimum number of confirmations (default to 6)
- `0x13` - Timestamp when any value in the the contract was last updated

The contract can be called with a couple commands. Note that you should convert the strings to integers yourself, as there is a dispute on the correct way of string padding in the various Ethereum clients (this will be resolved soon, hopefully, see https://github.com/ethereum/cpp-ethereum/issues/268)


### WATCH
Usage: `0x7761746368` `base58check_address`

A caller can request an address to be watched by the datafeed.

### GETRECEIVEDBYADDRESS
Usage: `0x6765747265636569766564627961646472657373` `base58check_address`

Returns an array with 2 elements; the `getreceivedbyaddress` value and the timestamp when this was last updated.

### SETRECEIVEDBYADDRESS
Usage: `0x7365747265636569766564627961646472657373` `base58check_address` `value`

Sets the `getreceivedbyaddress` value for the given address, can only be executed by the contract owner.

### SUICIDE
Usage: `0x73756963696465`

Allows the contract owner (creator) to remove the contract from the blockchain.

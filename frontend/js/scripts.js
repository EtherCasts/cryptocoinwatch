(function() {

    var cs = require('coinstring');
    var buffer = require('buffer');

    CryptoCoinWatch = {};

    CryptoCoinWatch.cmdWatch = "0x7761746368";

    CryptoCoinWatch.contractAddress = "0x987c1f13d417f7e04d852b44badc883e4e9782e1";

    CryptoCoinWatch.addressOffset = bigInt(2).pow(160);
    CryptoCoinWatch.addressRecordSize = bigInt(4);

    CryptoCoinWatch.getStatistics = function(contract) {
        return {
            owner: eth.stateAt(contract, "0x10"),
            source: eth.stateAt(contract, "0x11").bin(),
            minConfirmations: parseInt(eth.stateAt(contract, "0x12").dec()),
            lastUpdated: parseInt(eth.stateAt(contract, "0x13").dec()),
            watchListLength: parseInt(eth.stateAt(contract, "0x20").dec())
        };
    };

    CryptoCoinWatch.hexToAddress = function(hex) {
        var version;
        var hash;
        if (hex.length == 42) {
            version = 0;
            hash = new buffer.Buffer(hex.substring(2), 'hex');
        } else {
            version = parseInt(hex.substring(0, 4), 16);
            hash = new buffer.Buffer(hex.substring(4), 'hex');
        }
        var address = cs.encode(hash, version);
        return address.toString();
    };

    CryptoCoinWatch.epochFromNow = function(epoch) {
        if (epoch == 0 || typeof epoch === 'undefined') {
            return "never";
        } else {
            return moment.unix(epoch).fromNow();
        }
    };

    CryptoCoinWatch.getWatchList = function(contract) {
        var result = [];
        var watchListLength = parseInt(eth.stateAt(contract, "0x20").dec());

        for(var i = 0; i < watchListLength; i++) {
            var watchLocation = bigInt("0x20").add(i).add(1).toString();
            var addressHex = eth.stateAt(contract, watchLocation).hex();
            var btcAddress = CryptoCoinWatch.hexToAddress(addressHex);

            var addressIdx = CryptoCoinWatch.addressRecordSize.multiply(addressHex).plus(CryptoCoinWatch.addressOffset);

            var receivedByAddress = parseInt(eth.stateAt(contract, addressIdx.toString()).dec());
            var lastUpdated = parseInt(eth.stateAt(contract, addressIdx.add(1).toString()).dec());
            var nrWatched = parseInt(eth.stateAt(contract, addressIdx.add(2).toString()).dec());
            var lastWatched = parseInt(eth.stateAt(contract, addressIdx.add(3).toString()).dec());

            result.push({
                btcAddress: btcAddress,
                receivedByAddress: receivedByAddress,
                lastUpdated: lastUpdated,
                nrWatched: nrWatched,
                lastWatched: lastWatched
            });
        }
        return result;
    };

    CryptoCoinWatch.addressToHex = function(address) {
        var res = cs.decode(address);
        var hash = res.toString('hex');
        return '0x' + hash;
    };

    CryptoCoinWatch.watchAddress = function(contract, address) {
        var hex;
        try {
            hex = CryptoCoinWatch.addressToHex(address);
        } catch(err) {
            alert("Invalid address:" + err);
            return;
        }
        eth.transact(
            eth.key,
            "0",
            contract,
            CryptoCoinWatch.cmdWatch.pad(32) + hex.pad(32),
            "10000",
            eth.gasPrice,
            function() {
                alert("Address " + address +" is now watched");
            }
        );
    };
})();

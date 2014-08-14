(function($) {

    var cs = require('coinstring');
    var buffer = require('buffer');

    CryptoCoinWatch = {};

    CryptoCoinWatch.cmdWatch = "0x7761746368";

    //CryptoCoinWatch.contractAddress = "0xcd5805d60bbf9afe69a394c2bda10f6dae2c39af";
    CryptoCoinWatch.contractAddress = "0x83c5541a6c8d2dbad642f385d8d06ca9b6c731ee";

    CryptoCoinWatch.addressOffset = bigInt(2).pow(160);
    CryptoCoinWatch.addressRecordSize = bigInt(4);

    CryptoCoinWatch.getStatistics = function(contract) {
        return {
            owner: eth.stateAt(contract, "0x10"),
            source: eth.stateAt(contract, "0x11").bin(),
            minConfirmations: eth.stateAt(contract, "0x12").dec(),
            lastUpdated: eth.stateAt(contract, "0x13").dec(),
            watchList: eth.stateAt(contract, "0x20").dec()
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

    CryptoCoinWatch.showWatchList = function() {
        var watchList = eth.stateAt(CryptoCoinWatch.contractAddress, "0x20").dec();
        $("#watch-list").text(watchList);

        for(var i = 0; i < watchList; i++) {
            var watchLocation = bigInt("0x20").add(i).add(1).toString();
            var addressHex = eth.stateAt(CryptoCoinWatch.contractAddress, watchLocation).hex();
            var address = CryptoCoinWatch.hexToAddress(addressHex);

            var addressIdx = CryptoCoinWatch.addressRecordSize.multiply(addressHex).plus(CryptoCoinWatch.addressOffset);

            var receivedByAddress = eth.stateAt(CryptoCoinWatch.contractAddress, addressIdx.toString()).dec();
            var lastUpdated = eth.stateAt(CryptoCoinWatch.contractAddress, addressIdx.add(1).toString()).dec();
            var nrWatched = eth.stateAt(CryptoCoinWatch.contractAddress, addressIdx.add(2).toString()).dec();
            var lastWatched = eth.stateAt(CryptoCoinWatch.contractAddress, addressIdx.add(3).toString()).dec();

            $("#watch-table > tbody:last").append("<tr><td>" + address + "</td><td>" + receivedByAddress + "</td><td>" +
                    CryptoCoinWatch.epochFromNow(lastUpdated) + "</td><td>" + nrWatched + "</td><td>" +
                    CryptoCoinWatch.epochFromNow(lastWatched) + "</td></tr>");
        }
    };

    CryptoCoinWatch.addressToHex = function(address) {
        var res = cs.decode(address);
        var hash = res.toString('hex');
        return '0x' + hash;
    };

    CryptoCoinWatch.watchAddress = function() {
        var address = $("#address").val();
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
            CryptoCoinWatch.contractAddress,
            CryptoCoinWatch.cmdWatch.pad(32) + hex.pad(32),
            "10000",
            eth.gasPrice,
            function() {
                alert("Address " + address +" is now watched");
            }
        );
    };

    $(document).ready(function() {
        //try {
            //CryptoCoinWatch.showStatistics();
            //CryptoCoinWatch.showWatchList();
        //} catch(e) {
        //    $('#log').append(String(e) + "<br />");
        //}

        $("#btn-watch").click(function() {
            console.log("click");
            CryptoCoinWatch.watchAddress();
        });
    });

})(jQuery);

/** @jsx React.DOM */

var React = require("react");

/* global window */
// expost React globally for DevTools
window.React = React;

// Load jQuery, lodash and bootstrap
var jQuery = require("jquery");
window.$ = window.jQuery = jQuery;

var _ = require('lodash');
window._ = _;

require("bootstrap/dist/js/bootstrap.js");
require("bootstrap/dist/css/bootstrap.min.css");
require("bootstrap/dist/css/bootstrap-theme.min.css");

// eth.js compatibility
var bigInt = require("./js/eth/BigInteger.js");
window.bigInt = bigInt;

require("./js/eth/ethString.js");

/* global ethBrowser */
if (!ethBrowser) {
  var eth = require("./js/eth/eth.js");
  window.eth = eth;

  eth.stateAt = eth.storageAt;
  eth.messages = function() { return {}; };
  eth.toDecimal = function(x) { return x.dec(); };
  eth.fromAscii = function(x) { return x.unbin(); };
  eth.toAscii = function(x) { return x.bin().unpad(); };
  eth.pad = function(x, l) { return String(x).pad(l); };
  /*eth.oldtransact = function(i, c) { // a_s, f_v, t, d, g, p, f) {
    if (i.to === null) {
      var r = eth.transact(JSON.stringify(i.from));
      if (i.value)
        i.value(r);
    }
    else {
      console.log('POC 5 eth.transact is deprecated, tell DEV to fix eth.js');
      eth.transact(i.from, i.value, i.to, i.data, i.gas, i.gasPrice);
      if (f) f();
    }
  };*/
}

var CryptoCoinWatch = require("./CryptoCoinWatch");
var CryptoCoinWatchBox = require("./components/CryptoCoinWatchBox");

React.renderComponent(<CryptoCoinWatchBox contract={CryptoCoinWatch.contractAddress} pollInterval={5000} />,
        document.getElementById('container'));

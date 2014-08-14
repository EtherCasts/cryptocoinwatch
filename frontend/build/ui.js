/** @jsx React.DOM */

var StatisticsBox = React.createClass({displayName: 'StatisticsBox',
    render: function() {
        return (
            React.DOM.div({id: "statistics-box"}, 
                React.DOM.h3(null, "Statistics"), 
                React.DOM.ul(null, 
                    React.DOM.li(null, "Contract ", this.props.statistics.contract), 
                    React.DOM.li(null, "Owner: ", this.props.statistics.owner), 
                    React.DOM.li(null, "Source: ", this.props.statistics.source), 
                    React.DOM.li(null, "Min. Confirmations: ", this.props.statistics.minConfirmations), 
                    React.DOM.li(null, "Last Updated: ", moment.unix(this.props.statistics.lastUpdated).fromNow()), 
                    React.DOM.li(null, "Watch List: ", this.props.statistics.watchList)
                )
            )
        );
    }
});

var AddressRow = React.createClass({displayName: 'AddressRow',
    render: function() {
        return (
            React.DOM.tr(null, 
                React.DOM.td(null, this.props.address.btcAddress), 
                React.DOM.td(null, this.props.address.getreceivedbyaddress), 
                React.DOM.td(null, moment.unix(this.props.address.lastUpdated).fromNow()), 
                React.DOM.td(null, this.props.address.nrWatchers), 
                React.DOM.td(null, moment.unix(this.props.address.lastWatched).fromNow())
            )
        );
    }
});

var AddressTable = React.createClass({displayName: 'AddressTable',
    render: function() {
        var addressNodes = this.props.addresses.map(function (address) {
            return (
                AddressRow({address: address})
            );
        });
        return (
            React.DOM.table({id: "watch-table", className: "table"}, 
                React.DOM.thead(null, 
                    React.DOM.tr(null, 
                        React.DOM.th(null, "Address"), 
                        React.DOM.th(null, "getreceivedbyaddress"), 
                        React.DOM.th(null, "last updated"), 
                        React.DOM.th(null, "# watchers"), 
                        React.DOM.th(null, "last watched")
                    )
                ), 
                React.DOM.tbody(null, 
                    addressNodes
                )
            )
        );
    }
});

var WatchForm = React.createClass({displayName: 'WatchForm',
    render: function() {
        return (
            React.DOM.div({id: "watch-form"}, 
                React.DOM.h2(null, "Watch An Address"), 
                React.DOM.label({for: "address"}, "Which cryptocurrency address do you want to watch?"), 
                React.DOM.input({id: "address", type: "text", value: ""}), React.DOM.br(null), 
                React.DOM.button({id: "btn-watch"}, "WATCH")
            )
        );
    }
});

var CryptoCoinWatchUI = React.createClass({displayName: 'CryptoCoinWatchUI',
    render: function() {
        return (
            React.DOM.div({className: "spacer"}, 
                StatisticsBox({statistics: this.props.statistics}), 
                AddressTable({addresses: this.props.addresses}), 
                WatchForm(null)
            )
        );
    }
});

var statistics = {
    contract: '0xcd5805d60bbf9afe69a394c2bda10f6dae2c39af',
    owner: '0xcd2a3d9f938e13cd947ec05abc7fe734df8dd826',
    source: 'blockchain.info',
    minConfirmations: 6,
    lastUpdated: 1408010619,
    watchList: 4
};

var addresses = [{
    btcAddress: '36PrZ1KHYMpqSyAQXSG8VwbUiq2EogxLo2',
    getreceivedbyaddress: 2406330081938,
    lastUpdated: 1408010619,
    nrWatchers: 2,
    lastWatched: 1407405790
}, {
    btcAddress: '1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P',
    getreceivedbyaddress: 512129645662,
    lastUpdated: 1408010619,
    nrWatchers: 1,
    lastWatched: 1407405790
}, {
    btcAddress: '1CounterpartyXXXXXXXXXXXXXXXUWLpVr',
    getreceivedbyaddress: 213083765357,
    lastUpdated: 1408010619,
    nrWatchers: 0,
    lastWatched: 1407405790
}];

React.renderComponent(CryptoCoinWatchUI({statistics: statistics, addresses: addresses}), document.getElementById('container'));

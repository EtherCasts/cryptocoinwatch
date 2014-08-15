/** @jsx React.DOM */

var StatisticsBox = React.createClass({displayName: 'StatisticsBox',
    render: function() {
        return (
            React.DOM.div({className: "statisticsBox"}, 
                React.DOM.h3(null, "Statistics"), 
                React.DOM.ul(null, 
                    React.DOM.li(null, "Contract ", this.props.contract), 
                    React.DOM.li(null, "Owner: ", this.props.statistics.owner), 
                    React.DOM.li(null, "Source: ", this.props.statistics.source), 
                    React.DOM.li(null, "Min. Confirmations: ", this.props.statistics.minConfirmations), 
                    React.DOM.li(null, "Last Updated: ", CryptoCoinWatch.epochFromNow(this.props.statistics.lastUpdated)), 
                    React.DOM.li(null, "Watch list length: ", this.props.watchList.length)
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
                React.DOM.td(null, this.props.address.receivedByAddress), 
                React.DOM.td(null, CryptoCoinWatch.epochFromNow(this.props.address.lastUpdated)), 
                React.DOM.td(null, this.props.address.nrWatched), 
                React.DOM.td(null, CryptoCoinWatch.epochFromNow(this.props.address.lastWatched))
            )
        );
    }
});

var WatchList = React.createClass({displayName: 'WatchList',
    render: function() {
        var watchListNodes = this.props.watchList.map(function (address) {
            return (
                AddressRow({address: address})
            );
        });
        return (
            React.DOM.table({className: "watchList table"}, 
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
                    watchListNodes
                )
            )
        );
    }
});

var WatchForm = React.createClass({displayName: 'WatchForm',
    handleSubmit: function() {
        var address = this.refs.address.getDOMNode().value.trim();
        if (!address) {
            return false;
        }
        this.props.onWatchSubmit(address);
        this.refs.address.getDOMNode().value = '';
        return false;
    },
    render: function() {
        return (
            React.DOM.form({className: "watchForm", onSubmit: this.handleSubmit}, 
                React.DOM.h2(null, "Watch An Address"), 
                React.DOM.label({htmlFor: "address"}, "Which cryptocurrency address do you want to watch?"), React.DOM.br(null), 
                React.DOM.input({id: "address", ref: "address", type: "text", pattern: "^[a-km-zA-HJ-NP-Z1-9]{27,34}$", title: "Cryptocurrency address", placeholder: "Your address..."}), 
                React.DOM.input({type: "submit", value: "Watch"})
            )
        );
    }
});

var CryptoCoinWatchBox = React.createClass({displayName: 'CryptoCoinWatchBox',
    getInitialState: function() {
        return {statistics: {}, watchList: []};
    },
    handleWatchSubmit: function(address) {
        var watchList = this.state.watchList;
        var result = _.find(watchList, function(obj) { return obj.btcAddress === address });
        // do an optimistic updates if address is not yet present
        if (result.length == 0) {
            var newWatchList = watchList.concat([{btcAddress: address}]);
            this.setState({watchList: newWatchList});
        }
        CryptoCoinWatch.watchAddress(this.props.contract, address);
    },
    loadStatistics: function() {
        var statistics = CryptoCoinWatch.getStatistics(this.props.contract);
        this.setState({statistics: statistics});
    },
    loadWatchList: function() {
        var watchList = CryptoCoinWatch.getWatchList(this.props.contract);
        this.setState({watchList: watchList});
    },
    componentDidMount: function() {
        this.loadStatistics();
        this.loadWatchList();
        setInterval(this.loadStatistics, this.props.pollInterval);
        setInterval(this.loadWatchList, this.props.pollInterval);
    },
    render: function() {
        return (
            React.DOM.div({className: "cryptoCoinWatchBox"}, 
                StatisticsBox({contract: this.props.contract, statistics: this.state.statistics, watchList: this.state.watchList}), 
                WatchList({watchList: this.state.watchList}), 
                WatchForm({onWatchSubmit: this.handleWatchSubmit})
            )
        );
    }
});

React.renderComponent(CryptoCoinWatchBox({contract: CryptoCoinWatch.contractAddress, pollInterval: 5000}),
        document.getElementById('container'));

/** @jsx React.DOM */

var StatisticsBox = React.createClass({displayName: 'StatisticsBox',
    render: function() {
        return (
            React.DOM.div({id: "statistics-box"}, 
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
                    watchListNodes
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
                React.DOM.input({id: "address", type: "text"}), React.DOM.br(null), 
                React.DOM.button({id: "btn-watch"}, "WATCH")
            )
        );
    }
});

var CryptoCoinWatchBox = React.createClass({displayName: 'CryptoCoinWatchBox',
    getInitialState: function() {
        return {statistics: {}, watchList: []};
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
            React.DOM.div({className: "spacer"}, 
                StatisticsBox({contract: this.props.contract, statistics: this.state.statistics, watchList: this.state.watchList}), 
                WatchList({watchList: this.state.watchList}), 
                WatchForm(null)
            )
        );
    }
});

React.renderComponent(CryptoCoinWatchBox({contract: CryptoCoinWatch.contractAddress, pollInterval: 5000}),
        document.getElementById('container'));

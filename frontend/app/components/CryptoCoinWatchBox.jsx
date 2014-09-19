/** @jsx React.DOM */

var React = require("react");
var _ = require("lodash");

var CryptoCoinWatch = require("../CryptoCoinWatch");

var StatisticsBox = React.createClass({
    render: function() {
        return (
            <table className="statisticsBox table table-striped">
                <tbody>
                    <tr>
                        <th>Statistics</th>
                        <th />
                    </tr>
                    <tr>
                        <td>Contract</td>
                        <td>{this.props.contract}</td>
                    </tr>
                    <tr>
                        <td>Owner</td>
                        <td>{this.props.statistics.owner}</td>
                    </tr>
                    <tr>
                        <td>Source</td>
                        <td>{this.props.statistics.source}</td>
                    </tr>
                    <tr>
                        <td>Min. Confirmations</td>
                        <td>{this.props.statistics.minConfirmations}</td>
                    </tr>
                    <tr>
                        <td>Last Updated</td>
                        <td>{CryptoCoinWatch.epochFromNow(this.props.statistics.lastUpdated)}</td>
                    </tr>
                    <tr>
                        <td>Watch list length</td>
                        <td>{this.props.watchList.length}</td>
                    </tr>
                </tbody>
            </table>
        );
    }
});

var AddressRow = React.createClass({
    render: function() {
        return (
            <tr>
                <td>{this.props.address.btcAddress}</td>
                <td>{this.props.address.receivedByAddress}</td>
                <td>{CryptoCoinWatch.epochFromNow(this.props.address.lastUpdated)}</td>
                <td>{this.props.address.nrWatched}</td>
                <td>{CryptoCoinWatch.epochFromNow(this.props.address.lastWatched)}</td>
            </tr>
        );
    }
});

var WatchList = React.createClass({
    render: function() {
        var watchListNodes = this.props.watchList.map(function (address) {
            return (
                <AddressRow address={address} />
            );
        });
        return (
            <table className="watchList table table-striped">
                <thead>
                    <tr>
                        <th>Address</th>
                        <th>getreceivedbyaddress</th>
                        <th>last updated</th>
                        <th># watchers</th>
                        <th>last watched</th>
                    </tr>
                </thead>
                <tbody>
                    {watchListNodes}
                </tbody>
            </table>
        );
    }
});

var WatchForm = React.createClass({
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
            <div className="watchForm">
                <h2>Watch An Address</h2>
                <form onSubmit={this.handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="address">Which cryptocurrency address do you want to watch?</label>
                        <input id="address" ref="address" className="form-control" type="text" pattern="^[a-km-zA-HJ-NP-Z1-9]{27,34}$" title="Cryptocurrency address" placeholder="Your address..." />
                    </div>
                    <div className="form-group">
                        <input type="submit" value="Watch" className="btn btn-primary" />
                    </div>
                </form>
            </div>
        );
    }
});

var CryptoCoinWatchBox = React.createClass({
    getInitialState: function() {
        return {statistics: {}, watchList: []};
    },
    handleWatchSubmit: function(address) {
        var watchList = this.state.watchList;
        var result = _.find(watchList, function(obj) { return obj.btcAddress === address; });
        // do an optimistic updates if address is not yet present
        if (typeof result === "undefined") {
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
            <div className="cryptoCoinWatchBox">
                <h1>CryptoCoinWatch</h1>
                <StatisticsBox contract={this.props.contract} statistics={this.state.statistics} watchList={this.state.watchList} />
                <WatchList watchList={this.state.watchList} />
                <WatchForm onWatchSubmit={this.handleWatchSubmit} />
            </div>
        );
    }
});

module.exports = CryptoCoinWatchBox;

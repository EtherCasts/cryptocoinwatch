/** @jsx React.DOM */

var StatisticsBox = React.createClass({
    render: function() {
        return (
            <div className="statisticsBox">
                <h3>Statistics</h3>
                <ul>
                    <li>Contract {this.props.contract}</li>
                    <li>Owner: {this.props.statistics.owner}</li>
                    <li>Source: {this.props.statistics.source}</li>
                    <li>Min. Confirmations: {this.props.statistics.minConfirmations}</li>
                    <li>Last Updated: {CryptoCoinWatch.epochFromNow(this.props.statistics.lastUpdated)}</li>
                    <li>Watch list length: {this.props.watchList.length}</li>
                </ul>
            </div>
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
            <table className="watchList table">
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
    render: function() {
        return (
            <div className="watchForm">
                <h2>Watch An Address</h2>
                <label for="address">Which cryptocurrency address do you want to watch?</label>
                <input id="address" type="text" /><br />
                <button id="btn-watch">WATCH</button>
            </div>
        );
    }
});

var CryptoCoinWatchBox = React.createClass({
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
            <div className="cryptoCoinWatchBox">
                <StatisticsBox contract={this.props.contract} statistics={this.state.statistics} watchList={this.state.watchList} />
                <WatchList watchList={this.state.watchList} />
                <WatchForm />
            </div>
        );
    }
});

React.renderComponent(<CryptoCoinWatchBox contract={CryptoCoinWatch.contractAddress} pollInterval={5000} />,
        document.getElementById('container'));

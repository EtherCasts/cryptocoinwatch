/** @jsx React.DOM */

var StatisticsBox = React.createClass({
    render: function() {
        return (
            <div id="statistics-box">
                <h3>Statistics</h3>
                <ul>
                    <li>Contract {this.props.statistics.contract}</li>
                    <li>Owner: {this.props.statistics.owner}</li>
                    <li>Source: {this.props.statistics.source}</li>
                    <li>Min. Confirmations: {this.props.statistics.minConfirmations}</li>
                    <li>Last Updated: {moment.unix(this.props.statistics.lastUpdated).fromNow()}</li>
                    <li>Watch List: {this.props.statistics.watchList}</li>
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
                <td>{this.props.address.getreceivedbyaddress}</td>
                <td>{moment.unix(this.props.address.lastUpdated).fromNow()}</td>
                <td>{this.props.address.nrWatchers}</td>
                <td>{moment.unix(this.props.address.lastWatched).fromNow()}</td>
            </tr>
        );
    }
});

var AddressTable = React.createClass({
    render: function() {
        var addressNodes = this.props.addresses.map(function (address) {
            return (
                <AddressRow address={address} />
            );
        });
        return (
            <table id="watch-table" className="table">
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
                    {addressNodes}
                </tbody>
            </table>
        );
    }
});

var WatchForm = React.createClass({
    render: function() {
        return (
            <div id="watch-form">
                <h2>Watch An Address</h2>
                <label for="address">Which cryptocurrency address do you want to watch?</label>
                <input id="address" type="text" value=""/><br />
                <button id="btn-watch">WATCH</button>
            </div>
        );
    }
});

var CryptoCoinWatchUI = React.createClass({
    render: function() {
        return (
            <div className="spacer">
                <StatisticsBox statistics={this.props.statistics} />
                <AddressTable addresses={this.props.addresses} />
                <WatchForm />
            </div>
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

React.renderComponent(<CryptoCoinWatchUI statistics={statistics} addresses={addresses} />, document.getElementById('container'));

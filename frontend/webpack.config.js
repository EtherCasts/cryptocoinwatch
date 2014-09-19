var webpack = require("webpack");

module.exports = {
  entry: [
    "./app/app.jsx"
  ],
  output: {
    /* global __dirname */
    path: __dirname + "/app",
    filename: "bundle.js"
  },
  plugins: [
      new webpack.IgnorePlugin(/vertx/)
  ],
  resolve: {
    extensions: ['', '.js', '.jsx']
  },
  module: {
    loaders: [
      { test: /\.css$/, loader: "style!css" },
      { test: /\.less$/, loader: "style!css!less" },
      { test: /\.jsx$/, loaders: ["react-hot", "jsx"] },
      { test: /\.json$/, loader: "json" },
      { test: /\.woff$/,   loader: "url-loader?limit=10000&minetype=application/font-woff&name=assets/[name]-[hash].[ext]" },
      { test: /\.ttf$/,    loader: "file-loader?name=assets/[name]-[hash].[ext]" },
      { test: /\.eot$/,    loader: "file-loader?name=assets/[name]-[hash].[ext]" },
      { test: /\.svg$/,    loader: "file-loader?name=assets/[name]-[hash].[ext]" }
    ]
  }
};

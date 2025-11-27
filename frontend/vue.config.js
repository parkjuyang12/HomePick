module.exports = {
  devServer: {
    host: '0.0.0.0',
    port: 8080,
    client: {
      webSocketURL: 'auto://0.0.0.0:0/ws'
    }
  },
  configureWebpack: {
    watchOptions: {
      poll: 1000,
      ignored: /node_modules/
    }
  }
}
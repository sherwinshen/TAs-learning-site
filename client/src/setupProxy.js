const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
  app.use(
    createProxyMiddleware('/api', {
      target: "http://127.0.0.1:8080/", //配置你要请求的服务器地址
      changeOrigin: true,
      pathRewrite: {
        '^/api': '',
      },
    })
  );
};

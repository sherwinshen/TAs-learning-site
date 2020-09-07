const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
  app.use(
    createProxyMiddleware('/devApi', {
      target: "http://127.0.0.1:5000/", //配置你要请求的服务器地址
      changeOrigin: true,
      pathRewrite: {
        '^/devApi': '',
      },
    })
  );
};

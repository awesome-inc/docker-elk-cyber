const Hapi = require('hapi');
const server = new Hapi.Server();
server.connection({ host:'0.0.0.0', port: 3000 });

// Add server routes
require('./init')(server);

server.start((err) => {

  if (err) {
    throw err;
  }
  console.log('Server running at:', server.info.uri);
});

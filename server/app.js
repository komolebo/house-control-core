var http = require('http');

console.log("I'm running"); // TODO: remove

http.createServer(function (req, res) {
    res.writeHead(200, {'Content-Type': 'text/html'});
    res.write('Hello world');
    res.end();
}).listen(8080); asd
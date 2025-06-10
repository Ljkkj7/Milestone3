const express = require('express');
const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http);

app.use(express.static('public'));

io.on ('connection', (socket) => {
  console.log('A user connected');

});

http.listen(process.env.PORT || 3000);
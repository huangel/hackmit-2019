// libraries
const http = require('http');
const bodyParser = require('body-parser');
const session = require('express-session');
const express = require('express');
const path = require('path');
const socketio = require('socket.io');

// local dependencies
// const db = require('./db');
// const passport = require('./passport');
// const api = require('./routes/api');

// initialize express app
const app = express();
const publicPath = path.join(__dirname, '../client/dist');

// set POST request body parser
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

// set up sessions
app.use(session({
  secret: 'session-secret',
  resave: 'false',
  saveUninitialized: 'true'
}));

// // hook up passport
// app.use(passport.initialize());
// app.use(passport.session());

// app.get(['/profile/:user'], function (req, res) {
//   res.sendFile(path.join(__dirname, '../socket/dist', 'index.html'));
// });

// authentication routes
// app.get('/auth/google', passport.authenticate('google', { scope: ['profile'] }));

// app.get(
//   '/auth/google/callback',
//   passport.authenticate(
//     'google',
//     { failureRedirect: '/login' }
//   ),
//   function(req, res) {
//     res.redirect('/');
//   }
// );

// app.get('/logout', function(req, res) {
//   req.logout();
//   res.redirect('/'); 
// });

// app.use('/api', api );

// app.use(express.static('/client/dist'))

// app.get('/client/dist/js/{filename}', (req, res) => {
//     res.sendFile(req.filename, { root: "/Users/elizabethzhou/Documents/hackmit-2019/web/client/dist/" })
// });

app.use(express.static(publicPath));

app.get('/', (req, res) => {
    // res.send('Hello World!')
    res.sendFile('index.html', { root: "/Users/elizabethzhou/Documents/hackmit-2019/web/client/dist/" })
});

// 404 route
app.use(function(req, res, next) {
  const err = new Error('Not Found');
  err.status = 404;
  next(err);
});

// route error handler
app.use(function(err, req, res, next) {
  res.status(err.status || 500);
  res.send({
    status: err.status,
    message: err.message,
  });
});

// port config
const port = 3000; // config variable
const server = http.Server(app);

// socket stuff
const io = socketio(server);
app.set('socketio', io);

app.get('/start', (req, res) => {
  var spawn = require('child_process').spawn;
  var process = spawn('python', ['../client/src/get_mfcc.py']);
  for (var i = 0; i < process.length; i++) {
      io.on('connection', function (socket) {
          socket.emit('my response', {hello: process[i]});
      })
  }
})

server.listen(port, function() {
  console.log('Server running on port: ' + port);
});


// dependencies
const express = require('express');
const connect = require('connect-ensure-login');

const router = express.Router();

// api endpoints
router.get('/test', function(req, res) {
    res.send('quack');
});

// router.get('/whoami', function(req, res) {
//     if(req.isAuthenticated()) {
//         res.send(req.user);
//     }
//     else {
//         res.send({});
//     }
// });


// router.get('/user', function(req, res) {
//     User.findOne({ _id: req.query._id }, function(err, user) {
//         res.send(user);
//     });
// });

router.get('/listen', function(req, res) {
    var spawn = require("child_process").spawn;
    var process = spawn('python3', ["../../src/get_mfcc.py"]);

    process.stdout.on('data', function (data) {
        res.send(data.toString());
    });
});

router.post(
    '/message',
    connect.ensureLoggedIn(),
    function(req, res) {
        const newMessage = {
            'name': req.name,
            'message': req.message
        };

        const io = req.app.get('socketio');
        io.emit('message', {name: newMessage.name, message: newMessage.message});

        res.send({});
  }
);

// router.get('/comment', function(req, res) {
//     Comment.find({ parent: req.query.parent }, function(err, comments) {
//         res.send(comments);
//     })
// });

// router.post(
//     '/comment',
//     connect.ensureLoggedIn(),
//     function(req, res) {
//         const newComment = new Comment({
//             'creator_id': req.user._id,
//             'creator_name': req.user.name,
//             'parent': req.body.parent,
//             'content': req.body.content,
//         });

//         newComment.save(function(err, comment) {
//             // configure socket
//             const io = req.app.get('socketio');
//             io.emit("comment", { creator_name: req.user.name, parent: req.body.parent, content:req.body.content});
//             if (err) console.log(err);
//         });
//         res.send({});
//   }
// );
module.exports = router;

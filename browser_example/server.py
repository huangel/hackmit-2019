from flask import Flask, request, jsonify, send_file
import random
from get_mfcc import get_speaker
from flask_socketio import SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

help_queue = []
checkoff_queue = []


@app.route('/')
def index():
    index_file = 'index.html'
    return send_file(index_file)


@app.route('/index.js')
def js():
    js_file = './javascript/index.js'
    return send_file(js_file)

@app.route('/style.css')
def css():
    css_file = './static/style.css'
    return send_file(css_file)

# def messageReceived(methods=['GET', 'POST']):
#     print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    for x in get_speaker():
        print("getting speaker response:", x)
        socketio.emit('my response', x)
    # socketio.emit('my response', json, callback=messageReceived)

    
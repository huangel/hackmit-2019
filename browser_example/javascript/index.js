/**
 * Begins a stream with rev.ai using the AudioContext from the browser. Stream will continue until the websocket 
 * connection is closed. Follows the protocol specficied in our documentation:
 * https://www.rev.ai/docs/streaming
 */
function doStream() {
    statusElement = document.getElementById("status");
    tableElement = document.getElementById("messages");
    var site_base_url = 'http://localhost:5000/';
    finalsReceived = 0;
    currentCell = null;
    resetDisplay();
    statusElement.innerHTML = "Recording...";
    var socket = io.connect(site_base_url);
      socket.on( 'connect', function() {
        socket.emit( 'my event', {
          data: 'User Connected'
        } )
        // var form = $( 'status' ).on( 'submit', function( e ) {
        //   e.preventDefault()
        //   let user_name = $( 'input.username' ).val()
        //   let user_input = $( 'input.message' ).val()
        //   socket.emit( 'my event', {
        //     user_name : user_name,
        //     message : user_input
        //   } )
        //   $( 'input.message' ).val( '' ).focus()
        // } )
      } )
      socket.on( 'my response', function( msg ) {
        console.log( msg )
        onMessage(msg)
      })
    // audioContext = new (window.AudioContext || window.WebkitAudioContext)();
    // console.log("SAMPLERATE:" + audioContext.sampleRate)

    // const access_token = '02F4Okh0ju6Ug5Yq-VoSAsLRBdUVbD71P0m_-MoqBy4HJ0YjwHajPeQh4kFWqj4RZHBnacBJC-Tx7TAZ7ah6sPlnTim7Q';
    // const content_type = `audio/x-raw;layout=interleaved;rate=${audioContext.sampleRate};format=S16LE;channels=1`;
    // const baseUrl = 'wss://api.rev.ai/speechtotext/v1alpha/stream';
    // const query = `access_token=${access_token}&content_type=${content_type}`;
    
    // websocket = new WebSocket(`${site_baseUrl}`);

    // websocket.onopen = onOpen;
    // websocket.onclose = onClose;
    // websocket.onmessage = onMessage;
    // websocket.onerror = console.error;
}

/**
 * Gracefully ends the streaming connection with rev.ai. Signals and end of stream before closing and closes the 
 * browser's AudioContext
 */
function endStream() {
    if (websocket) {
        websocket.send("EOS");
        websocket.close();
    }
    if (audioContext) {
        audioContext.close();
    }

    var button = document.getElementById("streamButton");
    button.onclick = doStream;
    button.innerHTML = "Record";
}

// /**
//  * Updates the display and creates the link from the AudioContext and the websocket connection to rev.ai
//  * @param {Event} event 
//  */
// function onOpen(event) {
//     resetDisplay();
//     statusElement.innerHTML = "Opened";
//     navigator.mediaDevices.getUserMedia({ audio: true }).then((micStream) => {
//         audioContext.suspend();
//         var scriptNode = audioContext.createScriptProcessor(4096, 1, 1 );
//         var input = input = audioContext.createMediaStreamSource(micStream);
//         scriptNode.addEventListener('audioprocess', (event) => websocket.send("get speaker"));
//         input.connect(scriptNode);
//         scriptNode.connect(audioContext.destination);
//         audioContext.resume();
//     });
// }

/**
 * Displays the close reason and code on the webpage
 * @param {CloseEvent} event
 */
function onClose(event) {
    statusElement.innerHTML = `Closed with ${event.code}: ${event.reason}`;
}

/**
 * Handles messages received from the API according to our protocol
 * https://www.rev.ai/docs/streaming#section/Rev.ai-to-Client-Response
 * @param {MessageEvent} event
 */
function onMessage(data) {
    // var data = JSON.parse(event.data);
    switch (data.type){
        case "connected":
            statusElement.innerHTML =`Connected, job id is ${data.id}`;
            break;
        case "partial":
            currentCell.innerHTML = parseResponse(data);
            break;
        case "final":
            currentCell.innerHTML = parseResponse(data);
            if (data.type == "final"){
                finalsReceived++;
                var row = tableElement.insertRow(finalsReceived);
                currentCell = row.insertCell(0);
            }
            break;
        default:
            // We expect all messages from the API to be one of these types
            console.error("Received unexpected message");
            break;
    }
}

/**
 * Transform an audio processing event into a form suitable to be sent to the API. (S16LE or Signed 16 bit Little Edian).
 * Then send.
 * @param {AudioProcessingEvent} e 
 */
function processAudioEvent(e) {
    if (audioContext.state === 'suspended' || audioContext.state === 'closed' || !websocket) {
        return;
    }
    let inputData = e.inputBuffer.getChannelData(0);

    // The samples are floats in range [-1, 1]. Convert to PCM16le.
    let output = new DataView(new ArrayBuffer(inputData.length * 2));
    for (let i = 0; i < inputData.length; i++) {
        let multiplier = inputData[i] < 0 ? 0x8000 : 0x7fff; // 16-bit signed range is -32768 to 32767
        output.setInt16(i * 2, inputData[i] * multiplier | 0, true); // index, value, little edian
    }
    let intData = new Int16Array(output.buffer);
    // console.log("INT DATA:" + intData);
    let index = intData.length;
    while (index-- && intData[index] === 0 && index > 0) { }
    websocket.send(intData.slice(0, index + 1));
}

function parseResponse(response) {
    var message = "";
    var speaker = response.speaker ? response.speaker : "Unknown Speaker";
    message += response.type == "final" ?  speaker + ": " : `${speaker}: `;
    for (var i = 0; i < response.elements.length; i++){
        message += response.type == "final" ?  response.elements[i].value : `${response.elements[i].value} `;
    }
    return message;
}

function resetDisplay() {
    finalsReceived = 0;
    while(tableElement.hasChildNodes())
    {
        tableElement.removeChild(tableElement.firstChild);
    }
    var row = tableElement.insertRow(0);
    currentCell = row.insertCell(0);
}

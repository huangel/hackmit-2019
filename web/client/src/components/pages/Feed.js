import React from "react";
import Message from "../modules/Message.js";
import "../../css/app.css";
import io from 'socket.io-client';

export default class Feed extends React.Component {
    constructor(props) {
        super(props);

        this.socket = io('http://localhost:3000');
        
        this.state = {
            status: false,
            messages: [],
        }
    }

    parseResponse(response) {
        var message = "";
        var speaker = response.speaker ? response.speaker : "Unknown Speaker";
        message += response.type == "final" ?  speaker + ": " : `${speaker}: `;
        for (var i = 0; i < response.elements.length; i++){
            message += response.type == "final" ?  response.elements[i].value : `${response.elements[i].value}`;
        }
        return message;
    }

    componentDidMount() {
        this.socket.on('my response', (message) => {
            this.setState({
                messages: [{message}].concat(this.state.messages),
            });
        });

        document.title = "Listening...";
        this.getMessages();
    }


    render() {
        return (
            <div class="page-container feed">
                <div class="title">Listening...</div>
                {this.state.messages ? (
                    this.state.messages.map(messageObj => (
                        <Message name={messageObj.name} message={messageObj.message} />
                        )
                    )
                ) : (<div>No messages yet!</div>)}
            </div>
        );
    }

    getMessages = () => {
        return fetch(`/`)
            .then(res => res.json())
    };

    

}
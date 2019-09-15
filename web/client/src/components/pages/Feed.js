import React from "react";
import Message from "../modules/Message.js";
import "../../css/app.css";
import io from 'socket.io-client';

export default class Feed extends React.Component {
    constructor(props) {
        super(props);

        this.socket = io('http://localhost:3000');
        
        this.state = {
            messages: [],
        }
    }

    componentDidMount() {
        this.socket.on('message', (message) => {
            this.setState({
                messages: [{message}].concat(this.state.messages),
            });
        });

        document.title = "Listening";
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
        return fetch(`/api/listen`)
            .then(res => res.json())
    };

}
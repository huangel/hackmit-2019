import React from "react";
import "../../css/message.css";

export default class Message extends React.Component {
    constructor(props) {
      super(props);
    }

    render() {
        return (
            <div class="message-card">
                <div class="friend-name">{this.props.name}</div>
                <div class="message-text">{this.props.message}</div>
            </div>
        );
    }

}
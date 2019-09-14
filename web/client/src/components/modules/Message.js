import React from "react";
import "../../css/message.css";

export default class Message extends React.Component {
    constructor(props) {
      super(props);
    }
}

render() {
    return (
        <div class="message-card">
            <img class="friend-pic" src={this.props.pic} />
            <div class="friend-name" text={this.props.name} />
            <div class="message-text" text={this.props.message} />
        </div>
    );
}
import React from "react";
import Message from "../modules/Message.js";
import "../../css/app.css";

export default class Root extends React.Component {
    constructor(props) {
      super(props);
    }
}

render() {
    return (
      <div class="page-container">
        <div class="title">Conversations</div>
        <div class="subtitle">Start a conversation with...</div>
        <div class="container">
            <div class="tile-button">
                <img class="tile-image" src="./media/friends.jpg" />
                <div class="caption">your friends</div>
            </div>
            <div class="tile-button">
                <img class="tile-image" src="./media/stranger.jpg"/>
                <div class="caption">someone new</div>
            </div>
        </div>
        <Message pic="../../../client/dist/media/friends.jpg" name="Elizabeth Zhou" message="hi this is some words" />
      </div>
    );
}
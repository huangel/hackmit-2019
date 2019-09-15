import React from "react";
import Message from "../modules/Message.js";
import "../../css/app.css";

export default class Root extends React.Component {
    constructor(props) {
      super(props);
    }

  render() {
      return (
        <div class="page-container">
          <div class="title">Conversations</div>
          <a href="#" class="subtitle button">Start a conversation</a>
        </div>
      );
  }

}
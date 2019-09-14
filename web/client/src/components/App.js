import React from "react";
import "../css/app.css";
import Route from "react-router-dom/es/Route";
import Switch from "react-router-dom/es/Switch";
import Redirect from "react-router-dom/es/Redirect";


import NavBar from "./modules/NavBar";

import Root from "./pages/Root";
import Profile from "./pages/Profile";
import Leaderboard from "./pages/Leaderboard";
import GameContainer from "./pages/GameContainer";
import MapMaker from "./pages/MapMaker";
import ContactUs from "./pages/ContactUs";

import { TransitionGroup, CSSTransition } from "react-transition-group";


class App extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      userInfo: null,
      fetching: true,
    };
  }

  componentDidMount() {
    this.getUserInfo();
  }

  render() {
    const curPath = window.location.pathname;
    if (this.state.fetching) {
      return (null);
    }
    if (!this.state.userInfo && curPath != "/") {
      return <Redirect to="/" />;
    }
    return (
      <div>
        <NavBar userInfo={this.state.userInfo} logout={this.logout} />
          <Switch>
            <Route exact path="/" render={(props) => <Root {...props} userInfo={this.state.userInfo} />} />
            <Route exact path="/profile/:user_id" render={(props) => <Profile {...props} userInfo={this.state.userInfo} />} />
            <Route exact path="/leaderboards" render={(props) => <Leaderboard {...props} userInfo={this.state.userInfo} />} />
            <Route exact path="/play" render={(props) => <GameContainer {...props} userInfo={this.state.userInfo} refreshUserData={this.getUserInfo} />} />
            <Route exact path="/create" render={(props) => <MapMaker {...props} userInfo={this.state.userInfo} />} />
            <Route exact path="/contact_us" render={(props) => <ContactUs {...props} userInfo={this.state.userInfo} />} />
          </Switch>
      </div>
    );
  }

  logout = () => {
    this.setState({
      userInfo: null,
    });
  }

  getUserInfo = () => {
    fetch('/api/whoami')
    .then(res => res.json())
    .then(res => {
      if (!res._id) {
        this.setState({
          userInfo: null,
          fetching: false,
        })
      } else {
        fetch('/api/user?_id=' + res._id)
        .then(res => res.json())
        .then(userObj => {
          this.setState({
            userInfo: userObj,
            fetching: false,
          });
        });
      }
    });
  }
}

export default App;
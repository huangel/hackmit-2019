import React from "react";
// import "../css/app.css";
import Route from "react-router-dom/es/Route";
import Switch from "react-router-dom/es/Switch";
import Redirect from "react-router-dom/es/Redirect";

import Root from "./components/pages/Root";

class App extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      userInfo: null,
      fetching: true,
    };
  }

  render() {
    // const curPath = window.location.pathname;
    // if (this.state.fetching) {
    //   return (null);
    // }
    // if (!this.state.userInfo && curPath != "/") {
    //   return <Redirect to="/" />;
    // }
    return (
      <div>
          <Switch>
            <Route exact path="/" render={(props) => <Root {...props} />} />
          </Switch>
      </div>
    );
  }
}

export default App;
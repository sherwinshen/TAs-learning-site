import React, { Fragment } from "react";
import { HashRouter, Switch, Route } from "react-router-dom";
import "./styles/App.scss";
import Home from "./views/Home";
import LearnResult from "./views/LearnResult";

function App() {
  return (
    <Fragment>
      <HashRouter>
        <Switch>
          <Route component={Home} path="/" exact />
          <Route component={LearnResult} path="/result" exact />
        </Switch>
      </HashRouter>
    </Fragment>
  );
}

export default App;

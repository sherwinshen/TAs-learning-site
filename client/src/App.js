import React, { Fragment, Component } from "react";
import { HashRouter, Switch, Route } from "react-router-dom";
import "./styles/App.scss";
import Home from "./views/Home";
import LearnResult from "./views/LearnResult";
import intl from "react-intl-universal";

// locale data
const locales = {
  "en-US": require("./locales/en-US.json"),
  "zh-CN": require("./locales/zh-CN.json"),
};

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      initDone: false,
      lang: localStorage.getItem("lang_type") || "zh-CN",
    };
  }

  componentDidMount() {
    this.loadLocales();
  }

  loadLocales() {
    intl
      .init({
        currentLocale: this.state.lang,
        locales,
      })
      .then(() => {
        this.setState({ initDone: true });
      });
  }
  setLang = (value) => {
    localStorage.setItem("lang_type", value);
    window.location.reload(true);
  };

  render() {
    return (
      this.state.initDone && (
        <Fragment>
          <HashRouter>
            <Switch>
              <Route
                render={() => <Home setLang={this.setLang} />}
                path="/"
                exact
              />
              <Route
                render={() => <LearnResult setLang={this.setLang} />}
                path="/result"
                exact
              />
            </Switch>
          </HashRouter>
        </Fragment>
      )
    );
  }
}

export default App;

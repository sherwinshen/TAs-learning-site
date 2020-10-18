import React, { Component } from "react";
import { Divider } from "antd";
import { Result } from "antd";
import Automata from "../common/Automata";
import intl from "react-intl-universal";

class LearnFailModel extends Component {
  constructor(props) {
    super(props);
    this.state = {
      title: this.props.title,
      teacherType: this.props.teacherType,
      model: this.props.model,
    };
  }

  render() {
    return this.state.teacherType === "normalTeacher" ? (
      <div className="learn-fail module">
        <h4 className="module__title">{this.state.title}</h4>
        <Divider />
        <Result status="error" title={intl.get("learn-fail")} />
      </div>
    ) : (
      <div className="model-graph module">
        <h4 className="module__title">{this.state.title}</h4>
        <Divider />
        <div className="layer-container">
          <div className="layer">{intl.get("learn-fail-msg")}</div>
          <Automata
            model={this.state.model}
            width={"100%"}
            height={"400px"}
            isFull={true}
          />
        </div>
      </div>
    );
  }
}

export default LearnFailModel;

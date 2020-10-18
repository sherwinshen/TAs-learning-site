import React, { Component } from "react";
import { Result, Divider } from "antd";
import { LoadingOutlined } from "@ant-design/icons";
import Automata from "../common/Automata";
import intl from "react-intl-universal";

class ModelGraph extends Component {
  constructor(props) {
    super(props);
    this.state = {
      title: this.props.title,
      model: this.props.model,
      isFull: this.props.isFull
    };
  }

  static getDerivedStateFromProps(nextProps) {
    return { model: nextProps.model };
  }

  render() {
    return (
      <div className="model-graph module">
        <h4 className="module__title">{this.state.title}</h4>
        <Divider />
        {!this.state.model ? (
          <Result
            icon={<LoadingOutlined />}
            title={intl.get('learning')}
            subTitle={intl.get('wait-msg-2')}
          />
        ) : (
          <Automata model={this.state.model} width={"100%"} height={"400px"} isFull={true}/>
        )}
      </div>
    );
  }
}

export default ModelGraph;

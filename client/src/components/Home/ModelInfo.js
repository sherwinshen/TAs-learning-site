import React, { Component, Fragment } from "react";
import { Divider, Result, List } from "antd";
import Automata from "../common/Automata";
import intl from "react-intl-universal";

class ModelInfo extends Component {
  constructor(props) {
    super(props);
    this.state = {
      model: this.props.model,
    };
  }

  static getDerivedStateFromProps(nextProps) {
    return { model: nextProps.model };
  }

  removeModel = () => {
    this.props.deleteModel();
  };

  render() {
    let data;
    if (this.state.model) {
      data = [
        {
          title: intl.get("inputs"),
          content: this.state.model.inputs.toString(),
          color: "first ",
        },
        {
          title: intl.get("states"),
          content: this.state.model.states.toString(),
          color: "first ",
        },
        {
          title: intl.get("initState"),
          content: this.state.model.initState.toString(),
          color: "first ",
        },
        {
          title: intl.get("acceptStates"),
          content: this.state.model.acceptStates.toString(),
          color: "first ",
        },
      ];
    }
    return (
      <div className={"model-info module"}>
        <h4 className="module__title">{intl.get("modelInformation")}</h4>
        <Divider />
        {!this.state.model ? (
          <Result
            status="warning"
            title={intl.get("noData")}
            subTitle={intl.get("home-noDate-warn")}
          />
        ) : (
          <Fragment>
            <Automata
              model={this.state.model}
              removeModel={this.removeModel}
              isFull={true}
              width={"100%"}
              height={"450px"}
            />
            <Divider />
            <List
              grid={{ gutter: 16, column: 4 }}
              dataSource={data}
              renderItem={(item) => (
                <List.Item className="info-wrap">
                  <h2 className={`info-wrap__title color-${item.color}`}>
                    {item.title}
                  </h2>
                  <h4 className={`info-wrap__content`}>{item.content}</h4>
                </List.Item>
              )}
            />
          </Fragment>
        )}
      </div>
    );
  }
}

export default ModelInfo;

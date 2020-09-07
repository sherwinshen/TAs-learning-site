import React, { Component, Fragment } from "react";
import { Divider, Result, List } from "antd";
import Automata from "../common/Automata";

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

  render() {
    let data;
    if (this.state.model) {
      data = [
        {
          title: "Inputs",
          content: this.state.model.inputs.toString(),
          color: "second",
        },
        {
          title: "States",
          content: this.state.model.states.toString(),
          color: "second",
        },
        {
          title: "Init State",
          content: this.state.model.initState.toString(),
          color: "second",
        },
        {
          title: "Accept States",
          content: this.state.model.acceptStates.toString(),
          color: "second",
        },
      ];
    }
    return (
      <div className={"model-info module"}>
        <h4 className="module__title">模型信息</h4>
        <Divider />
        {!this.state.model ? (
          <Result
            title="暂无数据"
            subTitle="请先至「模型上传」处上传模型文件！"
          />
        ) : (
          <Fragment>
            <Automata
              model={this.state.model}
              width={"100%"}
              height={"450px"}
            />
            <List
              grid={{ gutter: 16, column: 4 }}
              dataSource={data}
              renderItem={(item) => (
                <List.Item className="info-wrap">
                  <div>
                    <span className={`info-wrap--circle bg-color-${item.color}`} />
                    <span className={`info-wrap--strip bg-color-${item.color}`} />
                  </div>
                  <h2 className={`info-wrap__title color-${item.color}`}> {item.title} </h2>
                  <h4 className={`info-wrap__content`}> {item.content}</h4>
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

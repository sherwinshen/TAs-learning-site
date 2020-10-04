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

  removeModel = () => {
    this.props.deleteModel();
  };

  render() {
    let data;
    if (this.state.model) {
      data = [
        {
          title: "系统行为集",
          content: this.state.model.inputs.toString(),
          color: "first ",
        },
        {
          title: "系统状态集",
          content: this.state.model.states.toString(),
          color: "first ",
        },
        {
          title: "初始状态",
          content: this.state.model.initState.toString(),
          color: "first ",
        },
        {
          title: "接受状态集",
          content: this.state.model.acceptStates.toString(),
          color: "first ",
        },
      ];
    }
    return (
      <div className={"model-info module"}>
        <h4 className="module__title">模型信息</h4>
        <Divider />
        {!this.state.model ? (
          <Result
            status="warning"
            title="暂无数据"
            subTitle="请先至右侧「模型上传」处上传包含模型信息的JSON文件，请严格按照格式说明！"
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
                  <h2 className={`info-wrap__title color-${item.color}`}>{item.title}</h2>
                  <h4 className={`info-wrap__content`}>
                    {item.content}
                  </h4>
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

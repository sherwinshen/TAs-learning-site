import React, { Component } from "react";
import {Divider, Empty} from "antd";
import MiddleModel from "./MiddleModel";

class LearnProcess extends Component {
  constructor(props) {
    super(props);
    this.state = {
      ifOmit: this.props.ifOmit,
      middleModels: this.props.middleModels,
      teacherType: this.props.teacherType,
    };
  }

  static getDerivedStateFromProps(nextProps) {
    return { middleModels: nextProps.middleModels, ifOmit: nextProps.ifOmit };
  }

  render() {
    return (
      <div className="learn-process module">
        <h4 className="module__title">学习过程</h4>
        <Divider />
        {this.state.teacherType === "smartTeacher" ? (
          <MiddleModel
            middleModels={this.state.middleModels}
            ifOmit={this.state.ifOmit}
          />
        ) : (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={"Normal Teacher 暂不支持学习过程展示!"}
          />
        )}
      </div>
    );
  }
}

export default LearnProcess;

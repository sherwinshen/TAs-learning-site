import React, { Component } from "react";
import { Button, Divider, Empty, message } from "antd";
import MiddleModel from "./MiddleModel";
import { GetMiddle } from "../../api";
import { getID } from "../../utils/session_storage";

class LearnProcess extends Component {
  constructor(props) {
    super(props);
    this.state = {
      ifOmit: this.props.ifOmit,
      middleModels: this.props.middleModels,
      teacherType: this.props.teacherType,
      isFinished: this.props.isFinished,
    };
  }

  static getDerivedStateFromProps(nextProps) {
    return {
      middleModels: nextProps.middleModels,
      ifOmit: nextProps.ifOmit,
      isFinished: nextProps.isFinished,
    };
  }

  getMiddle = () => {
    GetMiddle({ id: getID() })
      .then((response) => {
        const data = response.data;
        if (data.code === 0) {
          const a = document.createElement("a");
          const blob = new Blob([JSON.stringify(data.data)], {
            type: "application/json",
          });
          a.href = URL.createObjectURL(blob);
          a.download = "中间过程.json";
          a.click();
          message.success("下载成功！");
        } else {
          message.warning("下载失败！");
        }
      })
      .catch((error) => {
        console.log(error);
      });
  };

  render() {
    return (
      <div className="learn-process module">
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: "-10px",
          }}
        >
          <h4 className="module__title">学习过程</h4>
          {this.state.teacherType === "smartTeacher" ? (
            <Button
              type="primary"
              disabled={!this.state.isFinished}
              onClick={this.getMiddle}
            >
              下载中间过程
            </Button>
          ) : (
            <div />
          )}
        </div>
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

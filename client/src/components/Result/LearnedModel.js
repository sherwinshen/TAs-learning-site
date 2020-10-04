import React, { Component } from "react";
import { Result, Divider, Button } from "antd";
import { LoadingOutlined } from "@ant-design/icons";
import Automata from "../common/Automata";

class LearnedModel extends Component {
  constructor(props) {
    super(props);
    this.state = {
      title: this.props.title,
      model: this.props.model,
      isFull: this.props.isFull,
      isFinished: this.props.isFinished,
    };
  }

  static getDerivedStateFromProps(nextProps) {
    return { model: nextProps.model, isFinished: nextProps.isFinished };
  }

  getLearnedModel = () => {
    const svg = document.querySelector(".learned-model svg").outerHTML;
    const img = new Image();
    img.src =
      "data:image/svg+xml;base64," +
      window.btoa(unescape(encodeURIComponent(svg))); //svg内容中可以有中文字符
    img.onload = function () {
      const canvas = document.createElement("canvas");
      const context = canvas.getContext("2d");
      canvas.width = img.width;
      canvas.height = img.height;
      context.drawImage(img, 0, 0);
      const imgBase64 = canvas.toDataURL("image/png");
      const a = document.createElement("a");
      a.download = "结果模型.png";
      a.href = imgBase64;
      a.click();
    };
  };

  render() {
    return (
      <div className="model-graph learned-model module">
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: "-10px",
          }}
        >
          <h4 className="module__title">{this.state.title}</h4>
          <Button
            type="primary"
            disabled={!this.state.isFinished}
            onClick={this.getLearnedModel}
          >
            下载结果模型
          </Button>
        </div>

        <Divider />
        {!this.state.model ? (
          <Result
            icon={<LoadingOutlined />}
            title="学习中..."
            subTitle="请耐心等待"
          />
        ) : (
          <Automata
            model={this.state.model}
            width={"100%"}
            height={"400px"}
            isFull={true}
          />
        )}
      </div>
    );
  }
}

export default LearnedModel;

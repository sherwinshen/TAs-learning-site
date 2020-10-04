import React, { Component } from "react";
import { Divider, Spin, Row, Col, Button, message } from "antd";
import { LoadingOutlined } from "@ant-design/icons";
import { GetResult } from "../../api";
import { getID } from "../../utils/session_storage";

class LearnedResult extends Component {
  constructor(props) {
    super(props);
    this.state = {
      result: this.props.result,
      isFinished: this.props.isFinished,
      id: this.props.id,
    };
  }

  static getDerivedStateFromProps(nextProps) {
    return { result: nextProps.result, isFinished: nextProps.isFinished };
  }

  getResult = () => {
    GetResult({ id: getID() })
      .then((response) => {
        const data = response.data;
        if (data.code === 0) {
          const a = document.createElement("a");
          const blob = new Blob([JSON.stringify(data.data)], {
            type: "application/json",
          });
          a.href = URL.createObjectURL(blob);
          a.download = "学习结果.json";
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
    const antIcon = <LoadingOutlined style={{ fontSize: 24 }} spin />;
    let result = [];
    if (this.state.result) {
      for (let [key, value] of Object.entries(this.state.result)) {
        if (key === "result") {
          result.push(["学习结果", value]);
        } else if (key === "learningTime") {
          result.push(["学习时间", value]);
        } else if (key === "mqNum") {
          result.push(["成员查询数", value]);
        } else if (key === "eqNum") {
          result.push(["等价查询数", value]);
        } else if (key === "testNum") {
          result.push(["测试数", value]);
        } else if (key === "tables explored") {
          result.push(["观察表数", value]);
        } else if (key === "correct") {
          result.push(["是否正确", value]);
        } else if (key === "passingRate") {
          result.push(["验证集通过率", value]);
        }
      }
      result.sort(function (a, b) {
        // order是规则
        const order = [
          "学习结果",
          "学习时间",
          "成员查询数",
          "等价查询数",
          "测试数",
          "观察表数",
          "是否正确",
          "验证集通过率",
        ];
        return order.indexOf(a[0]) - order.indexOf(b[0]);
      });
    }

    return (
      <div className="learned-result module">
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: "-10px",
          }}
        >
          <h4 className="module__title">学习结果{this.state.isFinished}</h4>
          <Button
            type="primary"
            disabled={!this.state.isFinished}
            onClick={this.getResult}
          >
            下载学习结果
          </Button>
        </div>
        <Divider />
        {!this.state.result ? (
          <div className="text-align-center">
            <Spin tip="学习中..." indicator={antIcon} />
          </div>
        ) : (
          <Row>
            {result.map((item) => {
              return (
                <Col span={4} className="learned-result__item" key={item[0]}>
                  <h4 className="learned-result__title">{item[0]}</h4>
                  <span className="learned-result__subtitle">{item[1]}</span>
                </Col>
              );
            })}
          </Row>
        )}
      </div>
    );
  }
}

export default LearnedResult;

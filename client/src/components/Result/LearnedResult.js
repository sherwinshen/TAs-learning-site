import React, { Component } from "react";
import { Divider, Spin, Row, Col, Button, message } from "antd";
import { LoadingOutlined } from "@ant-design/icons";
import { GetResult } from "../../api";
import { getID } from "../../utils/session_storage";
import intl from "react-intl-universal";

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
          a.download = "learned-result.json";
          a.click();
          message.success(intl.get("download-success"));
        } else {
          message.warning(intl.get("download-fail"));
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
          result.push([intl.get("result"), value]);
        } else if (key === "learningTime") {
          result.push([intl.get("learningTime"), value]);
        } else if (key === "mqNum") {
          result.push([intl.get("mqNum"), value]);
        } else if (key === "eqNum") {
          result.push([intl.get("eqNum"), value]);
        } else if (key === "testNum") {
          result.push([intl.get("testNum"), value]);
        } else if (key === "tables explored") {
          result.push([intl.get("tablesExplored"), value]);
        } else if (key === "correct") {
          result.push([intl.get("correct"), value]);
        } else if (key === "passingRate") {
          result.push([intl.get("passingRate"), value]);
        }
      }
      result.sort(function (a, b) {
        // order是规则
        const order = [
          intl.get("result"),
          intl.get("learningTime"),
          intl.get("mqNum"),
          intl.get("eqNum"),
          intl.get("testNum"),
          intl.get("tablesExplored"),
          intl.get("correct"),
          intl.get("passingRate"),
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
          <h4 className="module__title">{intl.get("learnedResult")}</h4>
          <Button
            type="primary"
            disabled={!this.state.isFinished}
            onClick={this.getResult}
          >
            {intl.get("download-learnedResult")}
          </Button>
        </div>
        <Divider />
        {!this.state.result ? (
          <div className="text-align-center">
            <Spin tip={intl.get("learning")} indicator={antIcon} />
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

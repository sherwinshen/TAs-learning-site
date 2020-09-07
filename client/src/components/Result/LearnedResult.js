import React, { Component } from "react";
import { Divider, Spin, Row, Col } from "antd";
import { LoadingOutlined } from "@ant-design/icons";

class LearnedResult extends Component {
  constructor(props) {
    super(props);
    this.state = {
      result: this.props.result,
    };
  }

  static getDerivedStateFromProps(nextProps) {
    return { result: nextProps.result };
  }

  render() {
    const antIcon = <LoadingOutlined style={{ fontSize: 24 }} spin />;
    let result = [];
    if (this.state.result) {
      for (let [key, value] of Object.entries(this.state.result)) {
        result.push([key, value]);
      }
    }
    return (
      <div className="learned-result module">
        <h4 className="module__title">学习结果</h4>
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

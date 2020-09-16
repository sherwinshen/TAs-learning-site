import React, { Component } from "react";
import {Divider, Spin, Row, Col, Button, message} from "antd";
import { LoadingOutlined } from "@ant-design/icons";
import {GetResult} from "../../api";
import {getID} from "../../utils/session_storage";

class LearnedResult extends Component {
  constructor(props) {
    super(props);
    this.state = {
      result: this.props.result,
      isFinished: this.props.isFinished,
      id: this.props.id
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
          const a = document.createElement('a');
          const blob = new Blob([ JSON.stringify(data.data) ], {type : 'application/json'});
          a.href = URL.createObjectURL(blob);
          a.download = '学习结果.json'
          a.click();
          message.success("下载成功！");
        } else {
          message.warning("下载失败！");
        }
      })
      .catch((error) => {
        console.log(error);
      });
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
        <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '-10px'}}>
          <h4 className="module__title">学习结果{this.state.isFinished}</h4>
          <Button type="primary" disabled={!this.state.isFinished} onClick={this.getResult}>下载学习结果</Button>
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

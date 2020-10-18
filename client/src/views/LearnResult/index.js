import React, { Component } from "react";
import { withRouter } from "react-router-dom";
import Header from "../../components/Result/Header";
import {
  deleteID,
  deleteModel,
  deleteTeacher,
  deleteSetting,
  getID,
  getModel,
  getTeacher,
  getSetting,
} from "../../utils/session_storage";
import { message, Row, Col } from "antd";
import "./../../styles/result.scss";
import { Processing, Result, Delete } from "../../api";
import LearnProcess from "../../components/Result/LearnProcess";
import ModelGraph from "../../components/Result/ModelGraph";
import LearnedModel from "../../components/Result/LearnedModel";
import LearnedResult from "../../components/Result/LearnedResult";
import LearnFail from "../../components/Result/LearnFail";
import LearnFailModel from "../../components/Result/LearnFailModel";
import intl from "react-intl-universal";

let timer;

class LearnResult extends Component {
  constructor(props) {
    super(props);
    this.state = {
      setting: getSetting(),
      id: getID(),
      model: getModel(),
      middleModels: [],
      ifOmit: false,
      learnedModel: null,
      result: null,
      learnFlag: true,
      isFinished: false,
      lastModified: 0,
      teacherType: getTeacher(),
    };
  }

  componentDidMount() {
    if (!this.state.id) {
      message.warning(intl.get("upload-warn-3"));
      this.backToHome();
      return false;
    }
    this.initProcessing(this.state.id);
  }

  componentWillUnmount() {
    clearInterval(timer);
  }

  backToHome = () => {
    deleteID();
    deleteModel();
    deleteTeacher();
    deleteSetting();
    if (this.state.id) {
      // 删除后台的存储
      Delete({ id: this.state.id }).then(() => {});
    }
    this.props.history.push("/");
  };

  // 初始查询
  initProcessing = (id) => {
    Processing({ id, lastModified: this.state.lastModified })
      .then((response) => {
        const data = response.data;
        if (data.code === 1) {
          // 学习结束
          this.getResult(id);
          if (this.state.teacherType === "smartTeacher") {
            this.setState({
              middleModels: data.middleModels,
              ifOmit: data.ifOmit,
              lastModified: data.lastModified,
              isFinished: true,
            });
          } else {
            this.setState({
              lastModified: data.lastModified,
              isFinished: true,
            });
          }
        } else {
          this.getProcessing(id);
        }
      })
      .catch((error) => {
        console.log(error);
      });
  };

  // 开始轮询
  getProcessing = (id) => {
    timer = setInterval(() => {
      Processing({ id, lastModified: this.state.lastModified })
        .then((response) => {
          const data = response.data;
          if (data.code === 0) {
            // 更新学习过程
            if (this.state.teacherType === "smartTeacher") {
              this.setState({
                middleModels: data.middleModels,
                ifOmit: data.ifOmit,
                lastModified: data.lastModified,
              });
            } else {
              this.setState({
                lastModified: data.lastModified,
              });
            }
          } else if (data.code === 1) {
            // 学习结束
            if (this.state.teacherType === "smartTeacher") {
              this.setState({
                middleModels: data.middleModels,
                ifOmit: data.ifOmit,
                lastModified: data.lastModified,
                isFinished: true,
              });
            } else {
              this.setState({
                lastModified: data.lastModified,
                isFinished: true,
              });
            }
            clearInterval(timer);
            this.getResult(id);
          } else if (data.code === 2) {
            // 没有更新
          }
        })
        .catch((error) => {
          clearInterval(timer);
          console.log(error);
        });
    }, 3000);
  };

  // 获取结果
  getResult = (id) => {
    Result({ id })
      .then((response) => {
        const data = response.data;
        if (data.code === 0) {
          message.success(intl.get( "learn-success"));
          this.setState({
            learnedModel: data.learnedModel,
            result: data.result,
            learnFlag: true,
          });
        } else {
          message.warning(intl.get("learn-fail"));
          this.setState({
            learnFlag: false,
          });
        }
      })
      .catch((error) => {
        console.log(error);
      });
  };

  renderSetting = () => {
    let arr = Object.entries(this.state.setting);
    return (
      <Col span={24}>
        <div
          className="module"
          style={{ display: "flex", justifyContent: "space-between" }}
        >
          {arr.map((item) => {
            let key, value;
            if (item[0] === "timeout") {
              key = intl.get("timeout");
              value = item[1];
            } else if (item[0] === "upperGuard") {
              key = intl.get("GuardUpper");
              value = item[1];
            } else if (item[0] === "boxType") {
              key =intl.get("EqType");
              if (item[1] === "blackBox") {
                value = intl.get('PACTesting');
              } else {
                value = intl.get('exactEq');
              }
            } else if (item[0] === "teacherType") {
              key = intl.get('teacherType');
              if (item[1] === "smartTeacher") {
                value = "smart";
              } else {
                value = "normal";
              }
            } else if (item[0] === "epsilon") {
              key = intl.get('accuracy');
              value = item[1];
            } else if (item[0] === "delta") {
              key = intl.get('confidence');
              value = item[1];
            }
            return (
              <div key={item[0]} className="title">
                <span>{key}</span>: <span>{value}</span>
              </div>
            );
          })}
        </div>
      </Col>
    );
  };

  render() {
    return (
      <div className="result">
        <Header
          title={intl.get("resultTitle")}
          type="result"
          backToHome={this.backToHome}
          setLang={this.props.setLang}
        />
        <Row className="learn-result__wrap">
          {this.renderSetting()}
          <Col span={24}>
            <LearnProcess
              middleModels={this.state.middleModels}
              ifOmit={this.state.ifOmit}
              teacherType={this.state.teacherType}
              isFinished={this.state.isFinished}
            />
          </Col>
          <Col span={12}>
            <ModelGraph
              title={intl.get('init-model')}
              model={this.state.model}
              isFull={true}
            />
          </Col>
          <Col span={12}>
            {this.state.learnFlag ? (
              <LearnedModel
                title={intl.get('learned-model')}
                model={this.state.learnedModel}
                isFull={true}
                isFinished={this.state.isFinished}
              />
            ) : (
              <LearnFailModel
                title={intl.get('learned-model')}
                teacherType={this.state.teacherType}
                model={this.state.middleModels.slice(-1)[0]}
              />
            )}
          </Col>
          <Col span={24}>
            {this.state.learnFlag ? (
              <LearnedResult
                result={this.state.result}
                isFinished={this.state.isFinished}
              />
            ) : (
              <LearnFail title={intl.get("learned-result")} />
            )}
          </Col>
        </Row>
      </div>
    );
  }
}

export default withRouter(LearnResult);

import React, { Component, Fragment } from "react";
import { withRouter } from "react-router-dom";
import {
  Button,
  Divider,
  Form,
  InputNumber,
  message,
  Modal,
  Radio,
} from "antd";
import { Learning } from "../../api";
import {
  setID,
  setModel,
  setTeacher,
  setSetting,
} from "../../utils/session_storage";
import { getMinUpperGuard } from "../../utils/upperGuard";
import { QuestionCircleOutlined } from "@ant-design/icons";
import intl from "react-intl-universal";

class ModelSetting extends Component {
  constructor(props) {
    super(props);
    this.state = {
      boxType: "blackBox",
      teacherType: "smartTeacher",
      upperGuard: getMinUpperGuard(this.props.model),
      epsilon: 0.9,
      delta: 0.9,
      timeout: 1,
      minUpperGuard: getMinUpperGuard(this.props.model),
      model: this.props.model,
      visible: false,
    };
    this.formRef = React.createRef();
  }

  static getDerivedStateFromProps(nextProps) {
    return {
      upperGuard: getMinUpperGuard(nextProps.model),
      minUpperGuard: getMinUpperGuard(nextProps.model),
      model: nextProps.model,
    };
  }

  onChangeBoxType = (e) => {
    this.setState({
      boxType: e.target.value,
    });
  };

  onChangeTeacherType = (e) => {
    this.setState({
      teacherType: e.target.value,
    });
  };

  // 表单重置
  reset = () => {
    this.formRef.current.resetFields();
    this.setState({
      boxType: "blackBox",
      teacherType: "smartTeacher",
      upperGuard: 10,
      epsilon: 0.1,
      delta: 0.1,
      timeout: 1,
    });
  };

  // 请求失败
  fail = () => {
    message.error(intl.get("fail-msg-1"));
    this.reset();
    this.props.deleteModel();
  };

  onFinish = (values) => {
    if (!this.state.model) {
      message.error(intl.get("info-msg-1"));
      return false;
    }
    setSetting(values);
    values.model = this.state.model;
    values.epsilon = 1 - values.epsilon;
    values.delta = 1 - values.delta;
    Learning(values)
      .then((response) => {
        const data = response.data;
        if (data.code === 1) {
          message.success(intl.get("wait-msg-1"));
          // 将请求 id 存至 session localstorage
          setID(data.id);
          setModel(this.state.model);
          setTeacher(this.state.teacherType);
          this.props.history.push("/result");
        } else {
          this.fail();
        }
      })
      .catch(() => {
        this.fail();
      });
  };

  showInfo = () => {
    this.setState({
      visible: true,
    });
  };

  handleCancel = () => {
    this.setState({
      visible: false,
    });
  };

  render() {
    return (
      <div className="model-setting module">
        <div style={{ display: "flex" }}>
          <h4 className="module__title">{intl.get("parameterSettings")}</h4>
          <QuestionCircleOutlined
            onClick={this.showInfo}
            style={{ fontSize: "16px", marginTop: "6px", marginLeft: "6px" }}
          />
        </div>
        <Divider />
        <Form
          name="form"
          onFinish={this.onFinish}
          labelCol={{ span: 7 }}
          wrapperCol={{ span: 17 }}
          ref={this.formRef}
        >
          <Form.Item
            label={intl.get("EqType")}
            name="boxType"
            initialValue={"blackBox"}
          >
            <Radio.Group
              onChange={this.onChangeBoxType}
              value={this.state.boxType}
            >
              <Radio value={"blackBox"}>{intl.get("PACTesting")}</Radio>
              <Radio value={"whiteBox"}>{intl.get("exactEq")}</Radio>
            </Radio.Group>
          </Form.Item>
          <Form.Item
            label={intl.get("teacherType")}
            name="teacherType"
            initialValue={"smartTeacher"}
          >
            <Radio.Group
              onChange={this.onChangeTeacherType}
              value={this.state.teacherType}
            >
              <Radio value={"smartTeacher"}>Smart</Radio>
              <Radio value={"normalTeacher"}>Normal</Radio>
            </Radio.Group>
          </Form.Item>
          <Form.Item
            label={intl.get("timeout")}
            name="timeout"
            initialValue={5}
          >
            <InputNumber style={{ width: "90%" }} min={1} max={30} />
          </Form.Item>
          <Form.Item
            label={intl.get("GuardUpper")}
            name="upperGuard"
            initialValue={this.state.upperGuard}
          >
            <InputNumber
              style={{ width: "90%" }}
              min={this.state.minUpperGuard}
            />
          </Form.Item>
          {this.state.boxType === "blackBox" ? (
            <Fragment>
              <Form.Item
                label={intl.get("accuracy")}
                name="epsilon"
                initialValue={0.9}
              >
                <InputNumber style={{ width: "90%" }} min={0} max={1} />
              </Form.Item>
              <Form.Item
                label={intl.get("confidence")}
                name="delta"
                initialValue={0.9}
              >
                <InputNumber style={{ width: "90%" }} min={0} max={1} />
              </Form.Item>
            </Fragment>
          ) : null}
          <Form.Item style={{ justifyContent: "center", textAlign: "center" }}>
            <Button type="primary" htmlType="submit">
              {intl.get("start")}
            </Button>
            <Button style={{ marginLeft: "20px" }} onClick={this.reset}>
              {intl.get("reset")}
            </Button>
          </Form.Item>
        </Form>
        <Modal
          title={intl.get("parameterDescription")}
          visible={this.state.visible}
          onOk={this.handleCancel}
          onCancel={this.handleCancel}
          okText={intl.get("confirm")}
          cancelText={intl.get("cancel")}
          width={"40%"}
        >
          <p>{intl.get("parameter-msg-1")}</p>
          <p>{intl.get("parameter-msg-2")}</p>
          <p>
            {intl.get("parameter-msg-3")}
            <a
              href={"https://github.com/MrEnvision/pac_learn_DOTAs"}
              target="blank"
            >
              {intl.get("header-instruction-pac")}
            </a>
            {" " + intl.get("and") + " "}
            <a href={"https://github.com/Leslieaj/OTALearning"} target="blank">
              {intl.get("header-instruction-exact")}
            </a>
            。
          </p>
          <p>{intl.get("parameter-msg-4")}</p>
        </Modal>
      </div>
    );
  }
}

export default withRouter(ModelSetting);

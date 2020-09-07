import React, { Component, Fragment } from "react";
import { withRouter } from "react-router-dom";
import { Button, Divider, Form, InputNumber, message, Radio } from "antd";
import { Learning } from "../../api";
import { setID, setModel } from "../../utils/session_storage";

class ModelSetting extends Component {
  constructor(props) {
    super(props);
    this.state = {
      boxType: "blackBox",
      teacherType: "smartTeacher",
      upperGuard: 10,
      epsilon: 0.1,
      delta: 0.1,
      model: this.props.model,
    };
    this.formRef = React.createRef();
  }

  static getDerivedStateFromProps(nextProps) {
    return {
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
    });
  };

  // 请求失败
  fail = () => {
    message.error("请求失败，请重新设置！");
    this.reset();
    this.props.deleteModel();
  };

  onFinish = (values) => {
    if (!this.state.model) {
      message.error("Please upload the model first!");
      return false;
    }
    values.model = this.state.model;
    Learning(values)
      .then((response) => {
        const data = response.data;
        if (data.code === 1) {
          message.success("请求成功，正在学习中，请耐心等待！！");
          // 将请求 id 存至 session localstorage
          setID(data.id);
          // 将模型信息存储至 session localstorage
          setModel(this.state.model);
          this.props.history.push("/result");
        } else {
          this.fail();
        }
      })
      .catch(() => {
        this.fail();
      });
  };

  render() {
    return (
      <div className="model-setting module">
        <h4 className="module__title">参数设置</h4>
        <Divider />
        <Form
          name="form"
          onFinish={this.onFinish}
          labelCol={{ span: 7 }}
          wrapperCol={{ span: 17 }}
          ref={this.formRef}
        >
          <Form.Item label="Box Type" name="boxType" initialValue={"blackBox"}>
            <Radio.Group
              onChange={this.onChangeBoxType}
              value={this.state.boxType}
            >
              <Radio value={"blackBox"}>Black</Radio>
              <Radio value={"whiteBox"}>White</Radio>
            </Radio.Group>
          </Form.Item>
          <Form.Item
            label="Teacher Type"
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
          <Form.Item label="Guard 上界" name="upperGuard" initialValue={1}>
            <InputNumber style={{ width: "90%" }} min={1} />
          </Form.Item>
          {this.state.boxType === "blackBox" ? (
            <Fragment>
              <Form.Item
                label="Accuracy(0-1)"
                name="epsilon"
                initialValue={0.1}
              >
                <InputNumber style={{ width: "90%" }} min={0} max={1} />
              </Form.Item>
              <Form.Item
                label="Confidence(0-1)"
                name="delta"
                initialValue={0.1}
              >
                <InputNumber style={{ width: "90%" }} min={0} max={1} />
              </Form.Item>
            </Fragment>
          ) : null}
          <Form.Item style={{ justifyContent: "center", textAlign: "center" }}>
            <Button type="primary" htmlType="submit">
              开始学习
            </Button>
            <Button style={{ marginLeft: "20px" }} onClick={this.reset}>
              重置参数
            </Button>
          </Form.Item>
        </Form>
      </div>
    );
  }
}

export default withRouter(ModelSetting);

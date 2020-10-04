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
    message.error("请求失败，请重新设置！");
    this.reset();
    this.props.deleteModel();
  };

  onFinish = (values) => {
    if (!this.state.model) {
      message.error("请先上传模型!");
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
          message.success("请求成功，正在学习中，请耐心等待！！");
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
          <h4 className="module__title">参数设置</h4>
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
          <Form.Item label="模型类型" name="boxType" initialValue={"blackBox"}>
            <Radio.Group
              onChange={this.onChangeBoxType}
              value={this.state.boxType}
            >
              <Radio value={"blackBox"}>黑(灰)盒</Radio>
              <Radio value={"whiteBox"}>白盒</Radio>
            </Radio.Group>
          </Form.Item>
          <Form.Item
            label="学习类型"
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
          <Form.Item label="超时设置(min)" name="timeout" initialValue={1}>
            <InputNumber style={{ width: "90%" }} min={1} max={1000} />
          </Form.Item>
          <Form.Item
            label="Guard上界"
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
              <Form.Item label="精确度(0-1)" name="epsilon" initialValue={0.9}>
                <InputNumber style={{ width: "90%" }} min={0} max={1} />
              </Form.Item>
              <Form.Item label="置信值(0-1)" name="delta" initialValue={0.9}>
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
        <Modal
          title="参数说明"
          visible={this.state.visible}
          onOk={this.handleCancel}
          onCancel={this.handleCancel}
          okText={"确定"}
          cancelText={"取消"}
          width={"40%"}
        >
          <p>
            1. 模型类型分为黑(灰)盒与白盒，其中白盒表示学习算法知道系统原始模型，假设模型的等价查询可以直接判断是否等价；而黑(灰)盒表示学习算法并不直接知道系统原始模型或者仅有部分先验知识，算法仅能对系统进行输入并通过观察来判断行为是否接收与不接收，因此假设模型的等价查询我们通过PAC理论（准确度和置信度）来近似。
          </p>
          <p>
            2. 学习类型分为smart learning和normal learning，两者的区别在于smart learning假设在对系统进行输入的时候能够观察到内部时钟是否重置（参考watch dog），而normal learning我们假设不能直接获得系统内部时钟的重置信息，我们仅能够通过猜测重置情况来进行学习，这也极大增加了算法的复杂度。
          </p>
        </Modal>
      </div>
    );
  }
}

export default withRouter(ModelSetting);

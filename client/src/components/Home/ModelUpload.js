import React, { Component } from "react";
import { message, Divider, Row, Col, Button, Upload, Radio } from "antd";
import { EyeOutlined, UploadOutlined } from "@ant-design/icons";
import intl from "react-intl-universal";

class ModelUpload extends Component {
  constructor(props) {
    super(props);
    this.state = {
      fileList: [],
      model: null,
      exampleID: null,
    };
  }

  componentDidMount() {
    //通过pros接收父组件传来的方法
    this.props.onRef(this);
  }

  // 查看格式说明
  goToTemplate = () => {
    window.open("./model_template.html", "_blank");
  };

  // 上传模型文件
  upload = (file) => {
    if (file.type !== "application/json") {
      message.error(intl.get("upload-warn-1"));
      return false;
    }
    const reader = new FileReader();
    reader.readAsText(file, "UTF-8");
    reader.onload = (e) => {
      const fileValue = JSON.parse(e.target.result);
      if (!fileValue.acceptStates) {
        message.warning(intl.get("upload-warn-2"));
        return false;
      }
      if (!fileValue.trans) {
        message.warning(intl.get("upload-warn-2"));
        return false;
      }
      if (!fileValue.initState) {
        message.warning(intl.get("upload-warn-2"));
        return false;
      }
      if (!fileValue.states) {
        message.warning(intl.get("upload-warn-2"));
        return false;
      }
      if (!fileValue.inputs) {
        message.warning(intl.get("upload-warn-2"));
        return false;
      }
      message.success(intl.get("upload-success"));
      this.setState({
        fileList: [file],
        model: fileValue,
        exampleID: null,
      });
      this.props.setModel(fileValue);
    };
    return false;
  };

  // 删除文件
  remove = () => {
    this.setState({
      fileList: [],
      model: null,
    });
    this.props.setModel(null);
  };

  onChange = (e) => {
    const that = this;
    const value = e.target.value;
    const fileName = `./static/example-${value}.json`;
    const request = new XMLHttpRequest();
    request.open("get", fileName);
    request.send(null);
    request.onload = function () {
      if (request.status === 200) {
        const json = JSON.parse(request.responseText);
        message.success(`${intl.get("selected")}example-${value}!`);
        that.setState({
          model: json,
          fileList: [],
          exampleID: e.target.value,
        });
        that.props.setModel(json);
      }
    };
  };

  render() {
    return (
      <div className="model-upload module">
        <h4 className="module__title">{intl.get("modelUpload")}</h4>
        <Divider />
        <Radio.Group
          onChange={this.onChange}
          value={this.state.exampleID}
          style={{ marginBottom: "15px" }}
        >
          <Radio value={1}>Example-1</Radio>
          <Radio value={2}>Example-2</Radio>
          <Radio value={3}>Example-3</Radio>
          <Radio value={4}>Example-4</Radio>
        </Radio.Group>
        <Row gutter={20} style={{ marginBottom: "15px" }}>
          <Col span={10}>
            <Upload
              className="upload-btn"
              fileList={this.state.fileList}
              beforeUpload={this.upload}
              onRemove={this.remove}
            >
              <Button type="primary" icon={<UploadOutlined />} block>
                {intl.get("upload-model")}
              </Button>
            </Upload>
          </Col>
          <Col span={10}>
            <Button icon={<EyeOutlined />} block onClick={this.goToTemplate}>
              {intl.get("see-format")}
            </Button>
          </Col>
        </Row>
      </div>
    );
  }
}

export default ModelUpload;

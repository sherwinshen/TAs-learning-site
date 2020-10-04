import React, { Component } from "react";
import { message, Divider, Row, Col, Button, Upload } from "antd";
import { DownloadOutlined, UploadOutlined } from "@ant-design/icons";

class ModelUpload extends Component {
  constructor(props) {
    super(props);
    this.state = {
      fileList: [],
      model: null,
    };
  }

  componentDidMount() {
    //通过pros接收父组件传来的方法
    this.props.onRef(this);
  }

  // 下载模板文件
  download = () => {
    const a = document.createElement("a");
    a.href = "./static/model_template.md";
    a.download = "model_template.md";
    a.click();
  };

  // 上传模型文件
  upload = (file) => {
    if (file.type !== "application/json") {
      message.error("只支持 JSON 文件上传，可下载格式说明参考！");
      return false;
    }
    const reader = new FileReader();
    reader.readAsText(file, "UTF-8");
    reader.onload = (e) => {
      const fileValue = JSON.parse(e.target.result);
      if(!fileValue.acceptStates){
        message.warning("文件不符合模型格式，请重新上传!");
        return false
      }
      if(!fileValue.trans){
        message.warning("文件不符合模型格式，请重新上传!");
        return false
      }
      if(!fileValue.initState){
        message.warning("文件不符合模型格式，请重新上传!");
        return false
      }
      if(!fileValue.states){
        message.warning("文件不符合模型格式，请重新上传!");
        return false
      }
      if(!fileValue.inputs){
        message.warning("文件不符合模型格式，请重新上传!");
        return false
      }
      message.success("文件上传成功!");
      this.setState({
        fileList: [file],
        model: fileValue,
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

  render() {
    return (
      <div className="model-upload module">
        <h4 className="module__title">模型上传</h4>
        <Divider />
        <Row gutter={20} style={{ marginBottom: "15px" }}>
          <Col span={10}>
            <Upload
              className="upload-btn"
              fileList={this.state.fileList}
              beforeUpload={this.upload}
              onRemove={this.remove}
            >
              <Button type="primary" icon={<UploadOutlined />} block>
                上传模型文件
              </Button>
            </Upload>
          </Col>
          <Col span={10}>
            <Button icon={<DownloadOutlined />} block onClick={this.download}>
              下载格式说明
            </Button>
          </Col>
        </Row>
      </div>
    );
  }
}

export default ModelUpload;

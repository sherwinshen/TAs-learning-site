import React, { Component } from "react";
import {Button, Modal, Radio} from "antd";
import { ArrowLeftOutlined, InfoCircleOutlined } from "@ant-design/icons";
import intl from 'react-intl-universal';

class Header extends Component {
  constructor(props) {
    super(props);
    this.state = {
      type: this.props.type,
      title: this.props.title,
      langOptions: [
        { label: "中文", value: "zh-CN" },
        { label: "EN", value: "en-US" },
      ],
      visible: false,
      lang: localStorage.getItem("lang_type") || "zh-CN",
    };
  }

  showInfo = () => {
    this.setState({
      visible: true,
    });
  };

  handleCancel = (e) => {
    this.setState({
      visible: false,
    });
  };

  setLang = (e) => {
    const newLang = e.target.value;
    this.setState({
      lang: newLang,
    });
    this.props.setLang(newLang);
  };

  // showInfo = () => {
  //   Modal.info({
  //     width: "60%",
  //     maskClosable: true,
  //     okText: "关闭",
  //     title: "Basic Modal",
  //     content: (
  //       <div>
  //         <Divider />
  //         <div>hello</div>
  //       </div>
  //     )
  //   });
  // };

  render() {
    return (
      <div className="header">
        <Button
          shape="round"
          icon={<ArrowLeftOutlined />}
          onClick={this.props.backToHome}
          style={{ zIndex: 999 }}
        >
          返回首页
        </Button>
        <h1 className="header__title">{this.state.title}</h1>
        <div className="header__btn">
          <Button
            type="text"
            icon={<InfoCircleOutlined />}
            onClick={this.showInfo}
            style={{ marginRight: "10px" }}
          >
            使用说明
          </Button>
          <Radio.Group
            options={this.state.langOptions}
            onChange={this.setLang}
            value={this.state.lang}
            optionType="button"
            buttonStyle="solid"
            size="small"
          />
        </div>
        <Modal
          title="使用说明"
          visible={this.state.visible}
          onOk={this.handleCancel}
          onCancel={this.handleCancel}
          okText={"确定"}
          cancelText={"取消"}
          width={"60%"}
        >
          <p>
            如果网站使用出现错误，您也可以下载原型工具使用，下载地址：
            <a href={"https://github.com/MrEnvision/learning_OTA_by_testing"}>
              White Box Learning Tool
            </a>{" "}
            和{" "}
            <a href={"https://github.com/Leslieaj/OTALearningNormal"}>
              Black Box Learning Tool
            </a>
            。
          </p>
        </Modal>
      </div>
    );
  }
}

export default Header;

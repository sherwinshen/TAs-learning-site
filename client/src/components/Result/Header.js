import React, { Component } from "react";
import { Button, Radio } from "antd";
import { ArrowLeftOutlined, InfoCircleOutlined } from "@ant-design/icons";
import intl from "react-intl-universal";

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
      lang: localStorage.getItem("lang_type") || "zh-CN",
    };
  }

  showInfo = () => {
    window.open("./introduction.html", "_blank");
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
          {intl.get("backToHome")}
        </Button>
        <h1 className="header__title">{this.state.title}</h1>
        <div className="header__btn">
          <Button
            type="text"
            icon={<InfoCircleOutlined />}
            onClick={this.showInfo}
            style={{ marginRight: "10px" }}
          >
            {intl.get("instruction")}
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
      </div>
    );
  }
}

export default Header;

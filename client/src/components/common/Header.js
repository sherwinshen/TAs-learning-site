import React, { Component } from "react";
import { Button, Modal, Radio } from "antd";
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
      visible: false,
      lang: localStorage.getItem("lang_type") || "zh-CN",
    };
  }

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
        <img
          src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYwIiBoZWlnaHQ9IjE0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBjbGFzcz0iaWNvbkFib3ZlIj4KIDwhLS0tLT4KIDxkZWZzPgogIDwhLS0tLT4KICA8bGluZWFyR3JhZGllbnQgeTI9IjAlIiB4Mj0iMTAwJSIgeTE9IjAlIiB4MT0iMCUiIGlkPSJjYWNjYTEwYi0yYzBmLTQxODktYjYzYy0zNGYxMWRjMzdhYTgiIGdyYWRpZW50VHJhbnNmb3JtPSJyb3RhdGUoMjUpIj4KICAgPHN0b3Agc3RvcC1jb2xvcj0iIzMyNzBGRiIgb2Zmc2V0PSIwJSIvPgogICA8c3RvcCBzdG9wLWNvbG9yPSIjMzJBQkZGIiBvZmZzZXQ9IjEwMCUiLz4KICA8L2xpbmVhckdyYWRpZW50PgogPC9kZWZzPgogPGRlZnM+CiAgPCEtLS0tPgogPC9kZWZzPgoKIDwhLS0tLT4KIDxnPgogIDx0aXRsZT5iYWNrZ3JvdW5kPC90aXRsZT4KICA8cmVjdCBmaWxsPSJub25lIiBpZD0iY2FudmFzX2JhY2tncm91bmQiIGhlaWdodD0iMTQyIiB3aWR0aD0iMTYyIiB5PSItMSIgeD0iLTEiLz4KIDwvZz4KIDxnPgogIDx0aXRsZT5MYXllciAxPC90aXRsZT4KICA8ZyB0cmFuc2Zvcm09Im1hdHJpeCgyLjg0NTY1OTk0OTk4ODMwNCwwLDAsMi44NDU2NTk5NDk5ODgzMDQsOTIuMjc4NDA5NDIyNzU2MDMsMTMwLjM0Njk4NzAyNTczKSAiIGZpbGw9InVybCgjY2FjY2ExMGItMmMwZi00MTg5LWI2M2MtMzRmMTFkYzM3YWE4KSIgaWQ9IjNhNjYyMDE1LWQ1YzAtNGQ0NS05YzU1LWExM2ZhMWY4OTYwMSI+CiAgIDxzd2l0Y2ggdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMCwtNi43MDI2NTgxOTczNTUwNDllLTcpIHRyYW5zbGF0ZSgwLC02LjcwMjY1ODE5NzM1NTA0OWUtNykgdHJhbnNsYXRlKC05LjQ4ODEzNDM4NDE1NTI3MywwKSB0cmFuc2xhdGUoLTE1LjExMDczMDE3MTIwMzYxMywwKSB0cmFuc2xhdGUoMCwxLjIyMjM3MDUwNTMzMjk0NjgpIHRyYW5zbGF0ZSgzLjg2NTUzNjkyODE3Njg4LDApIHRyYW5zbGF0ZSgtMTAuMTkwOTU4MDIzMDcxMjg5LDAuMzUxNDEyMzI2MDk3NDg4NCkgdHJhbnNsYXRlKDAsNS45MDQ5OTQ5NjQ1OTk2MDkpIHRyYW5zbGF0ZSgwLC01LjkwNDk5NDk2NDU5OTYwOSkgdHJhbnNsYXRlKDAsLTUuOTA0OTk0OTY0NTk5NjA5KSB0cmFuc2xhdGUoMCwtNS45MDQ5OTQ5NjQ1OTk2MDkpIHRyYW5zbGF0ZSgwLC01LjkwNDk5NDk2NDU5OTYwOSkgdHJhbnNsYXRlKDAsLTUuOTA0OTk0OTY0NTk5NjA5KSB0cmFuc2xhdGUoMCwtNS45MDQ5OTQ5NjQ1OTk2MDkpIHRyYW5zbGF0ZSgwLC01LjkwNDk5NDk2NDU5OTYwOSkgdHJhbnNsYXRlKDAsLTUuOTA0OTk0OTY0NTk5NjA5KSB0cmFuc2xhdGUoMCwtNS45MDQ5OTQ5NjQ1OTk2MDkpIHRyYW5zbGF0ZSgtMC41OTA0OTk1MjAzMDE4MTg4LC0wLjU5MDQ5OTUyMDMwMTgxODgpICI+CiAgICA8ZyBpZD0ic3ZnXzMiPgogICAgIDxwYXRoIGlkPSJzdmdfNCIgZD0ibTE1LjMsMTUuOWMtMC44LDAgLTEuNSwtMC4zIC0yLjEsLTAuOWwtMS40LC0xLjRsNC4yLC00LjNsMS40LDEuNGMwLjYsMC42IDAuOSwxLjMgMC45LDIuMXMtMC4zLDEuNiAtMC45LDIuMWMtMC41LDAuNyAtMS4zLDEgLTIuMSwxem0tMC43LC0yLjNjMC40LDAuNCAxLDAuNCAxLjQsMGMwLjIsLTAuMiAwLjMsLTAuNCAwLjMsLTAuN2MwLC0wLjMgLTAuMSwtMC41IC0wLjMsLTAuN2wtMS40LDEuNHoiLz4KICAgICA8cGF0aCBpZD0ic3ZnXzUiIGQ9Im0xNy40NDIsMTMuNTI3bDYuMzM0LDYuMTA5bC0xLjM4OCwxLjQ0bC02LjMzNSwtNi4xMWwxLjM4OSwtMS40Mzl6bTE1LjkxNywxNS42NjNsNS40NDQsNS40NDRsLTEuNDE0LDEuNDE0bC01LjQ0NCwtNS40NDRsMS40MTQsLTEuNDE0eiIvPgogICAgIDxwYXRoIGlkPSJzdmdfNiIgZD0ibTM4LjEsNDAuNGMtMS4zLDAgLTIuNiwtMC41IC0zLjUsLTEuNWwtNi4xLC02LjFsMS40LC0xLjRsNi4xLDYuMWMxLjIsMS4yIDMuMSwxLjIgNC4yLDBjMS4yLC0xLjIgMS4yLC0zLjEgMCwtNC4ybC02LjEsLTYuMWwxLjQsLTEuNGw2LjEsNi4xYzIsMiAyLDUuMSAwLDcuMWMtMSwwLjkgLTIuMiwxLjQgLTMuNSwxLjR6Ii8+CiAgICAgPGcgaWQ9InN2Z183Ij4KICAgICAgPHBhdGggaWQ9InN2Z184IiBkPSJtMzQuOCwyNC4zYy0xLjksMCAtMy42LC0wLjcgLTUsLTIuMXMtMi4xLC0zLjEgLTIuMSwtNC45YzAsLTEuOSAwLjcsLTMuNiAyLjEsLTVsMS44LC0xLjhsMS40LDEuNGwtMS44LDEuOGMtMC45LDAuOSAtMS41LDIuMiAtMS41LDMuNXMwLjUsMi42IDEuNSwzLjVzMi4yLDEuNSAzLjUsMS41YzEuMywwIDIuNiwtMC41IDMuNSwtMS41bDEuOCwtMS44bDEuNCwxLjRsLTEuOCwxLjhjLTEuMSwxLjUgLTIuOSwyLjIgLTQuOCwyLjJ6Ii8+CiAgICAgIDxwYXRoIGlkPSJzdmdfOSIgZD0ibTQxLjYsMjAuNWwtMi4xLC0yLjFsLTAuNywwLjZjLTAuOCwwLjggLTEuOCwxLjIgLTIuOCwxLjJjLTEuMSwwIC0yLjEsLTAuNCAtMi44LC0xLjJjLTAuOCwtMC44IC0xLjIsLTEuOCAtMS4yLC0yLjhjMCwtMS4xIDAuNCwtMi4xIDEuMiwtMi44bDAuNywtMC43bC0yLjEsLTIuMWwxLjQsLTEuNGwzLjUsMy41bC0yLjEsMi4xYy0wLjQsMC40IC0wLjYsMC45IC0wLjYsMS40czAuMiwxIDAuNiwxLjRzMC45LDAuNiAxLjQsMC42YzAuNSwwIDEsLTAuMiAxLjQsLTAuNmwyLjEsLTIuMWwzLjUsMy41bC0xLjQsMS41em0tMjYuMiwxNC4zbDIsMGwwLDJsLTIsMGwwLC0yeiIvPgogICAgICA8ZyBpZD0ic3ZnXzEwIj4KICAgICAgIDxwYXRoIGlkPSJzdmdfMTEiIGQ9Im0yNS45MSwyMS43MzdsMy45ODIsMy45MzdsLTEuNDA2LDEuNDIzbC0zLjk4MiwtMy45MzhsMS40MDYsLTEuNDIyeiIvPgogICAgICA8L2c+CiAgICAgIDxnIGlkPSJzdmdfMTIiPgogICAgICAgPHBhdGggaWQ9InN2Z18xMyIgZD0ibTE2LjMsNDAuOWMtMS4zLDAgLTIuNiwtMC41IC0zLjUsLTEuNWMtMC45LC0wLjkgLTEuNSwtMi4yIC0xLjUsLTMuNXMwLjUsLTIuNiAxLjUsLTMuNWwwLjEsLTAuMWwxMC4zLC03LjVsMS4yLDEuNmwtMTAuMyw3LjVjLTAuNSwwLjYgLTAuOCwxLjMgLTAuOCwyLjFzMC4zLDEuNiAwLjksMi4xYzEuMSwxLjEgMy4xLDEuMSA0LjIsMC4xbDcuNSwtMTAuM2wxLjYsMS4ybC03LjYsMTAuNWMtMSwwLjcgLTIuMiwxLjMgLTMuNiwxLjN6Ii8+CiAgICAgIDwvZz4KICAgICA8L2c+CiAgICA8L2c+CiAgIDwvc3dpdGNoPgogIDwvZz4KIDwvZz4KPC9zdmc+"
          alt="logo"
          className="header__logo"
        />
        <h1 className="header__title">{this.state.title}</h1>
        <div className="header__btn">
          {this.state.type !== "home" ? (
            <Button
              shape="round"
              icon={<ArrowLeftOutlined />}
              onClick={this.props.backToHome}
            >
              {intl.get("backToHome")}
            </Button>
          ) : null}
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
        <Modal
          title={intl.get("instruction")}
          visible={this.state.visible}
          onOk={this.handleCancel}
          onCancel={this.handleCancel}
          okText={intl.get("confirm")}
          cancelText={intl.get("cancel")}
          width={"60%"}
        >
          <p>
            {intl.get("header-instruction-1")}
            <a
              href={"https://github.com/MrEnvision/learning_OTA_by_testing"}
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
        </Modal>
      </div>
    );
  }
}

export default Header;

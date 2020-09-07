import React, {Component} from "react";
import {withRouter} from "react-router-dom";
import Header from "../../components/common/Header";
import {getToken} from "../../utils/token";
import {message} from "antd";

class LearnResult extends Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  backToHome = () => {
    this.props.history.push('/');
  };

  componentDidMount() {
    if (!getToken()) {
      message.warning('请先上传模型并配置参数！')
      this.backToHome()
    }
  }

  render() {
    return (
      <div className="result">
        <Header
          title="Learning Result"
          type="result"
          backToHome={this.backToHome}
        />
      </div>
    );
  }
}

export default withRouter(LearnResult);

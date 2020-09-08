import React, {Component} from 'react';
import {Divider} from "antd";
import {Result} from "antd";

class LearnFail extends Component {
  constructor(props) {
    super(props);
    this.state = {
      title: this.props.title
    };
  }

  render() {
    return (
      <div className='learn-fail module'>
        <h4 className="module__title">{this.state.title}</h4>
        <Divider/>
        <Result
          status="error"
          title="学习失败，请重试！"
        />
      </div>
    )
  }
}

export default LearnFail;
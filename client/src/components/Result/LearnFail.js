import React, {Component} from 'react';
import {Divider} from "antd";
import {Result} from "antd";
import intl from "react-intl-universal";

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
          title={intl.get("learn-fail")}
        />
      </div>
    )
  }
}

export default LearnFail;
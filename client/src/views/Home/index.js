import React, { Component } from "react";
import { Row, Col } from "antd";
import "./../../styles/home.scss";
import Header from "../../components/common/Header";
import ModelInfo from "../../components/Home/ModelInfo";
import ModelUpload from "../../components/Home/ModelUpload";
import ModelSetting from "../../components/Home/ModelSetting";
import { deleteToken } from "../../utils/token";

class Home extends Component {
  constructor(props) {
    super(props);
    this.state = {
      model: null,
    };
  }

  componentDidMount() {
    deleteToken();
  }

  onRef = (ref) => {
    this.modelUpload = ref
  }

  setModel = (value) => {
    this.setState({ model: value });
  };

  deleteModel = () => {
    this.modelUpload.remove()
  };

  render() {
    return (
      <div className="home">
        <Header title="Timed Automata Learning Tool" type="home" />
        <Row className="home__wrap">
          <Col span={15} className="home__wrap--left">
            <ModelInfo model={this.state.model} />
          </Col>
          <Col span={9} className="home__wrap--right">
            <ModelUpload setModel={this.setModel} onRef={this.onRef} />
            <ModelSetting
              model={this.state.model}
              deleteModel={this.deleteModel}
            />
          </Col>
        </Row>
      </div>
    );
  }
}

export default Home;

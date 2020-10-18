import React, {Component, Fragment} from "react";
import {Spin, Row, Col, Result} from "antd";
import {LoadingOutlined, EllipsisOutlined} from "@ant-design/icons";
// import { Swiper, SwiperSlide } from "swiper/react";
// import SwiperCore, { Navigation } from "swiper";
// import "swiper/swiper.scss";
// import "swiper/components/navigation/navigation.scss";
import Automata from "../common/Automata";
import intl from "react-intl-universal";
// SwiperCore.use([Navigation]);

class MiddleModel extends Component {
  constructor(props) {
    super(props);
    this.state = {
      ifOmit: this.props.ifOmit,
      middleModels: this.props.middleModels,
    };
  }

  static getDerivedStateFromProps(nextProps) {
    return {middleModels: nextProps.middleModels, ifOmit: nextProps.ifOmit};
  }

  render() {
    const middleModels = this.state.middleModels;
    // const preView = middleModels.length;
    const antIcon = <LoadingOutlined style={{fontSize: 24}} spin/>;
    return (
      <div className="middle-model">
        {this.state.middleModels.length === 0 ? (
          <div className="text-align-center">
            <Spin tip={intl.get('learning')} indicator={antIcon} />
          </div>
        ) : (
          <div className="middle-model__content">
            <Row justify="space-around">
              {this.state.ifOmit ? (
                <Fragment>
                  {middleModels.slice(0, 2).map((item, index) => (
                    <Col key={index} span={4}>
                      <Automata model={item} width={"100%"} height={"200px"} />
                    </Col>
                  ))}
                  <Col key={2} span={4}>
                    <Result icon={<EllipsisOutlined />} />
                  </Col>
                  {middleModels.slice(2).map((item, index) => (
                    <Col key={index + 3} span={4}>
                      <Automata model={item} width={"100%"} height={"200px"} />
                    </Col>
                  ))}
                </Fragment>
              ) : (
                middleModels.map((item, index) => (
                  <Col key={index} span={4}>
                    <Automata model={item} width={"100%"} height={"200px"} />
                  </Col>
                ))
              )}
            </Row>
          </div>
        )}
      </div>
    );
  }
}

export default MiddleModel;

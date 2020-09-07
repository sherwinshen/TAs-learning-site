import React, { Component } from "react";
import {Divider, Spin} from "antd";
import { LoadingOutlined } from "@ant-design/icons";
import { Swiper, SwiperSlide } from "swiper/react";
import SwiperCore, { Navigation } from "swiper";
import "swiper/swiper.scss";
import "swiper/components/navigation/navigation.scss";
import Automata from "../common/Automata";

SwiperCore.use([Navigation]);

class MiddleModel extends Component {
  constructor(props) {
    super(props);
    this.state = {
      middleModels: this.props.middleModels,
    };
  }

  render() {
    const preView = this.state.middleModels.length >= 5 ? 5 : this.state.middleModels.length;
    const antIcon = <LoadingOutlined style={{ fontSize: 24 }} spin />;
    return (
      <div className="middle-model module">
        <h4 className="module__title">学习过程</h4>
        <Divider />
        {this.state.middleModels.length === 0 ? (
          <div className="text-align-center">
            <Spin tip="学习中..." indicator={antIcon} />
          </div>
        ) : (
          <div className="middle-model__content">
            <Swiper spaceBetween={30} slidesPerView={preView} navigation>
              {this.state.middleModels.map((item, index) => (
                <SwiperSlide key={index}>
                  <Automata model={item} width={"100%"} height={"250px"} />
                </SwiperSlide>
              ))}
            </Swiper>
          </div>
        )}
      </div>
    );
  }
}

export default MiddleModel;

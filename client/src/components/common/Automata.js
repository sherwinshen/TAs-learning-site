import React from "react";
import { Graphviz } from "graphviz-react";
// import { Modal } from "antd";
// import {ZoomInOutlined } from '@ant-design/icons';

function Automata(props) {
  if (!props.model) {
    return false;
  }

  const initState = props.model.initState;
  const acceptStates = props.model.acceptStates;

  let states = props.model.states.map((item) => {
    if (acceptStates.indexOf(item) !== -1) {
      return `${item} [label=${item} shape=doublecircle]`;
    }
    return `${item} [label=${item}]`;
  });
  if (props.isFull) {
    states.push(`start [shape=plaintext]`);
  }
  states = states.join(" ");

  let trans = Object.values(props.model.trans).map((item) => {
    return `${item[0]} -> ${item[4]} [label=" ${item[1]}, ${item[2]}, ${
      item[3] === "n" || item[3] === false ? "false" : "true"
    }"]`;
  });
  if (props.isFull) {
    trans.push(`start -> ${initState} [style=dashed]`);
  }
  trans = trans.join(" ");

  const options = {
    height: props.height,
    width: props.width,
  };

  // const zoom = function () {
  //   Modal.info({
  //     width: "80%",
  //     maskClosable: true,
  //     icon: <ZoomInOutlined />,
  //     okText: 'Close',
  //     content: (
  //       <Graphviz
  //         dot={`digraph { ${states} ${trans} }`}
  //         options={{
  //           height: "65vh",
  //           width: "100%",
  //         }}
  //       />
  //     ),
  //   });
  // };

  return (
    <div className="automata">
      <Graphviz dot={`digraph { ${states} ${trans} }`} options={options} />
    </div>
  );
}

export default Automata;

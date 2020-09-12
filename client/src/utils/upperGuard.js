export function getMinUpperGuard(model) {
  if(!model) return 0
  const guards = [];
  const trans = Object.values(model.trans);
  for (let i = 0; i < trans.length; i++) {
    guards.push(trans[i][2]);
  }
  let max = 0;
  for (let i = 0; i < guards.length; i++) {
    const guardsTemp = guards[i].split("U");
    for (let j = 0; j < guardsTemp.length; j++) {
      let temp1 = guardsTemp[j].split(",")[1];
      temp1 = temp1.slice(0, temp1.length - 1);
      if (temp1 !== "+") {
        max = Math.max(max, Number(temp1) + 1);
      }
      let temp2 = guardsTemp[j].split(",")[0];
      temp2 = temp2.slice(1, temp2.length);
      max = Math.max(max, Number(temp2) + 1);
    }
  }
  return max;
}

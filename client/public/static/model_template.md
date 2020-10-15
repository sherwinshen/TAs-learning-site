## TA模型文件说明

请严格按照格式说明构建您所想要学习的时间自动机模型的JSON文件，然后上传至系统进行学习。注意，目前系统仅支持学习**确定性单时钟自动机**（Deterministic One-clock Timed Automata）。

### 格式说明：

- "states": the set of the name of locations;
- "inputs": the input alphabet;
- "trans": the set of transitions in the form `id : [name of the source location, input action, guards, reset, name of the target location];`
  - "+" in a guard means INFTY;
  - "r" means resetting the clock, "n" otherwise
- "initState": the name of initial location;
- "acceptStates": the set of the name of accepting locations.

#### 模型举例：

```json
{
	"inputs": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
	"states": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"],
	"trans": {
		"0": ["1", "a", "[0,+)", "r", "2"],
		"1": ["1", "j", "[0,+)", "r", "4"],
		"2": ["2", "f", "[1,+)", "r", "1"],
		"3": ["2", "b", "[0,2]", "n", "3"],
		"4": ["2", "c", "[0,1]", "n", "4"],
		"5": ["3", "e", "[0,5]", "r", "5"],
		"6": ["3", "f", "[0,+)", "r", "6"],
		"7": ["4", "b", "[0,2]", "n", "3"],
		"8": ["4", "d", "[0,5]", "r", "5"],
		"9": ["4", "f", "[1,+)", "r", "1"],
		"10": ["5", "f", "[0,+)", "n", "6"],
		"11": ["5", "g", "[0,+)", "n", "7"],
		"12": ["6", "g", "[0,4)", "n", "8"],
		"13": ["6", "h", "[0,3)", "n", "9"],
		"14": ["7", "f", "[0,+)", "n", "11"],
		"15": ["8", "h", "[0,7)", "r", "10"],
		"16": ["9", "g", "[0,7)", "r", "10"],
		"17": ["10", "i", "[2,2]", "r", "1"],
		"18": ["11", "h", "[2,7)", "r", "1"]
	},
	"initState": "1",
	"acceptStates": ["1", "5"]
}
```

---

如有疑问，请邮箱联系 👉 [EnvisionShen@gmail.com](mailto:EnvisionShen@gmail.com)
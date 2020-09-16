#  模型学习工具站点

模型学习工具站点主要用于参加 [NASAC2020软件研究成果原型系统竞赛](http://chinasoft2020.cqu.edu.cn/jstz/rjyjcgyxxtjs.htm)，目前仅支持 One-clock-timed-automata 模型学习。本项目由开发者版权所有，未经允许不得商用。

## 1. 项目结构

### 1.1 前端模块

技术栈：React + Ant Design + axios + [graphviz-react](https://www.npmjs.com/package/graphviz-react) (用于自动机绘制) 

### 1.2 后端模块

技术栈：flask + flask_cors + gunicorn + supervisor + Nginx

### 1.3 接口设计

<img src="./接口图.png" style="zoom:80%;" />

## 2. 成果支撑

### 2.1 相关论文

1. Shen W, An J, Zhan B, et al. PAC Learning of Deterministic One-Clock Timed Automata (Accepted by ICFEM2020)
2. An J, Chen M, Zhan B, et al. Learning One-Clock Timed Automata[C]//International Conference on Tools and Algorithms for the Construction and Analysis of Systems. Springer, Cham, 2020: 444-462. [[Paper](https://link.springer.com/chapter/10.1007/978-3-030-45190-5_25)] [[Full version on arXiv](https://arxiv.org/pdf/1910.10680.pdf)] 

### 2.2 原型工具

1. [OTALearning](https://github.com/Leslieaj/OTALearning) / [OTALearningNormal](https://github.com/Leslieaj/OTALearningNormal): This prototype tool is dedicated to actively learning deterministic one-clock timed automata (DOTAs). (The evaluated artifact by TACAS-2020 is also archived in the [Figshare repository](https://doi.org/10.6084/m9.figshare.11545983.v3).)
2. [OTALearning_by_Testing](https://github.com/MrEnvision/learning_OTA_by_testing): This prototype tool is dedicated to actively learning DOTAs under more realistic assumptions within the framework of PAC learning. 

# adk-demos
代码主要来自[Agent Development Kit 中文文档](https://adk.wiki/)，为了适配DashScope，做了一些改动。

## 环境准备
1. 安装Python
2. 安装uv
```
pip install uv
```
3. 使用uv初始化依赖环境
```
cd adk-demos
uv sync
```
4. 激活环境
```
.venv\Scripts\activate
```

## Agents

### 1. my_agent
提供mock的时间查询工具供agent调用

[参考文档](https://adk.wiki/get-started/python/#create-an-agent-project)


### 2. multi_tool_agent
提供纽约的时间查询工具以及mock的天气工具供agent调用

[参考文档](https://adk.wiki/get-started/quickstart/#create-agent-project)


### 3. weather_agent_v1
在my_agent的基础上，添加了session和runner

[参考文档](https://adk.wiki/tutorials/agent-team/#step-your-first-agent-basic-weather-lookup)


### 4. weather_agent_team
在weather_agent_v1的基础上，添加sub-agent、防护callback、状态ToolContext等功能。

```
cd weather_agent_team
uv run main.py
```

[参考文档](https://adk.wiki/tutorials/agent-team/#step-building-an-agent-team-delegation-for-greetings-farewells)


## 常用adk命令
创建智能体项目
```
adk create my_agent
```

通过命令行界面运行
```
adk run my_agent
```

通过网页界面运行
```
adk web --port 8000
```

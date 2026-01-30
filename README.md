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

```
adk run my_agent
```

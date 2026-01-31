import asyncio
from dotenv import load_dotenv

from google.genai import types
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService



load_dotenv()

def get_weather(city: str) -> dict:
    """获取指定城市的当前天气报告。

    Args:
        city (str): 城市名称（例如，"New York"、"London"、"Tokyo"）。

    Returns:
        dict: 包含天气信息的字典。
              包含一个 'status' 键（'success' 或 'error'）。
              如果是 'success'，包含 'report' 键与天气详情。
              如果是 'error'，包含 'error_message' 键。
    """
    print(f"--- 工具：get_weather 被调用，城市：{city} ---") # 记录工具执行
    city_normalized = city.lower().replace(" ", "") # 基本标准化

    # 模拟天气数据
    mock_weather_db = {
        "newyork": {"status": "success", "report": "纽约的天气是晴朗的，温度为 25°C。"},
        "london": {"status": "success", "report": "伦敦多云，温度为 15°C。"},
        "tokyo": {"status": "success", "report": "东京有小雨，温度为 18°C。"},
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"抱歉，我没有 '{city}' 的天气信息。"}


# 工具使用示例（可选测试）
# print(get_weather("New York"))
# print(get_weather("Paris"))


weather_agent = Agent(
    name="weather_agent_v1",
    model=LiteLlm(model='dashscope/deepseek-v3.2'),
    description="为特定城市提供天气信息。",
    instruction="你是一个有用的天气助手。"
                "当用户询问特定城市的天气时，"
                "使用 'get_weather' 工具查找信息。"
                "如果工具返回错误，礼貌地告知用户。"
                "如果工具成功，清晰地呈现天气报告。",
    tools=[get_weather], # 直接传递函数
)


# --- 会话管理 ---
# 关键概念：SessionService 存储对话历史和状态。
# InMemorySessionService 是本教程的简单、非持久存储。
session_service = InMemorySessionService()

# 定义用于标识交互上下文的常量
APP_NAME = "weather_tutorial_app"
USER_ID = "user_1"
SESSION_ID = "session_001" # 为简单起见使用固定 ID

async def init_session(app_name:str,user_id:str,session_id:str) -> InMemorySessionService:
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    print(f"会话已创建：App='{app_name}'，User='{user_id}'，Session='{session_id}'")
    return session

session = asyncio.run(init_session(APP_NAME,USER_ID,SESSION_ID))

# --- Runner ---
# 关键概念：Runner 编排智能体执行循环。
runner = Runner(
    agent=weather_agent, # 我们要运行的智能体
    app_name=APP_NAME,   # 将运行与我们的应用关联
    session_service=session_service # 使用我们的会话管理器
)
print(f"已为智能体 '{runner.agent.name}' 创建 Runner。")


async def call_agent_async(query: str, runner, user_id, session_id):
  """向智能体发送查询并打印最终响应。"""
  print(f"\n>>> 用户查询：{query}")

  # 以 ADK 格式准备用户的消息
  content = types.Content(role='user', parts=[types.Part(text=query)])

  final_response_text = "智能体没有产生最终响应。" # 默认值

  # 关键概念：run_async 执行智能体逻辑并产生事件。
  # 我们遍历事件以找到最终答案。
  async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
      # 你可以取消注释下面的行以查看执行期间的*所有*事件
      # print(f"  [事件] 作者：{event.author}，类型：{type(event).__name__}，最终：{event.is_final_response()}，内容：{event.content}")

      # 关键概念：is_final_response() 标记轮次的结束消息。
      if event.is_final_response():
          if event.content and event.content.parts:
             # 假设第一部分中的文本响应
             final_response_text = event.content.parts[0].text
          elif event.actions and event.actions.escalate: # 处理潜在错误/升级
             final_response_text = f"智能体升级：{event.error_message or '无特定消息。'}"
          # 如果需要，在这里添加更多检查（例如，特定错误代码）
          break # 找到最终响应后停止处理事件

  print(f"<<< 智能体响应：{final_response_text}")


async def run_conversation():
    await call_agent_async("伦敦的天气如何？",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

    await call_agent_async("巴黎怎么样？",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID) # 期望工具的错误消息

    await call_agent_async("告诉我纽约的天气",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)
    

if __name__ == "__main__":
    try:
        asyncio.run(run_conversation())
    except Exception as e:
        print(f"发生错误：{e}")

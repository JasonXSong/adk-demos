from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


load_dotenv()
# Mock 工具实现
def get_current_time(city: str) -> dict:
    """返回指定城市中的当前时间。"""
    return {"status": "success", "city": city, "time": "10:30 AM"}

root_agent = Agent(
    model=LiteLlm(model='dashscope/deepseek-v3.2'),
    name='my_agent',
    description="报告指定城市的当前时间。",
    instruction="你是一个有用的助手，可以报告城市的当前时间。为此使用 'get_current_time' 工具。",
    tools=[get_current_time]
)

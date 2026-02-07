from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


from tools import say_hello, say_goodbye, get_weather_stateful
from callbacks import block_keyword_guardrail, block_paris_tool_guardrail


def create_greeting_agent() -> Agent:
    """
    创建一个简单的问候智能体。
    """
    return Agent(
        model = LiteLlm(model='dashscope/deepseek-v3.2'),
        name="greeting_agent",
        instruction="你是问候智能体。你的唯一任务是向用户提供友好的问候。"
                    "使用 'say_hello' 工具生成问候。"
                    "如果用户提供了他们的名字，确保将其传递给工具。"
                    "不要参与任何其他对话或任务。",
        description="使用 'say_hello' 工具处理简单的问候和打招呼。", # 对委托至关重要
        tools=[say_hello],
    )


def create_farewell_agent() -> Agent:
    """
    创建一个简单的告别智能体。
    """
    return Agent(
        model = LiteLlm(model='dashscope/deepseek-v3.2'),
        name="farewell_agent",
        instruction="你是告别智能体。你的唯一任务是提供礼貌的告别消息。"
                    "当用户表示他们要离开或结束对话时使用 'say_goodbye' 工具"
                    "（例如，使用 'bye'、'goodbye'、'thanks bye'、'see you' 等词）。"
                    "不要执行任何其他操作。",
        description="使用 'say_goodbye' 工具处理简单的告别和再见。", # 对委托至关重要
        tools=[say_goodbye],
    )


def create_weather_agent_with_safety():
    """
    创建一个具有安全保护的天气智能体。
    """
    greeting_agent = create_greeting_agent()
    farewell_agent = create_farewell_agent()

    return Agent(
        name="weather_agent_v6_tool_guardrail",
        model=LiteLlm(model='dashscope/deepseek-v3.2'),
        description="主智能体：处理天气，委托，包括输入和工具防护。",
        instruction="你是主要的天气智能体。使用 'get_weather_stateful' 提供天气。"
                    "将问候委托给 'greeting_agent'，将告别委托给 'farewell_agent'。"
                    "仅处理天气、问候和告别。",
        tools=[get_weather_stateful],
        sub_agents=[greeting_agent, farewell_agent],
        output_key="last_weather_report",
        before_model_callback=block_keyword_guardrail, # 输入防护
        before_tool_callback=block_paris_tool_guardrail # <<< 工具防护
    )

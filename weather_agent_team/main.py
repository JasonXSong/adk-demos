import asyncio
from dotenv import load_dotenv

from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agents import create_weather_agent_with_safety


async def call_agent_async(query: str, runner, user_id, session_id):
    """
    向智能体发送查询并打印最终响应。
    """
    print(f"\n>>> 用户查询：{query}")

    # 以 ADK 格式准备用户的消息
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "智能体没有产生最终响应。" # 默认值

    # 关键概念：run_async 执行智能体逻辑并产生事件。
    # 我们遍历事件以找到最终答案。
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # 你可以取消注释下面的行以查看执行期间的*所有*事件
        print(f"  [事件] 作者：{event.author}，类型：{type(event).__name__}，最终：{event.is_final_response()}，内容：{event.content}")

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


async def run_team_conversation():
    APP_NAME = "weather_tutorial_agent_team"
    USER_ID = "user_1_agent_team"
    SESSION_ID = "session_001_agent_team"

    """运行完整的演示对话。"""
    print("=== 初始化 ===")
    # 1. 创建会话服务和带初始状态的会话
    session_service = InMemorySessionService()
    initial_state = {"user_preference_temperature_unit": "Celsius"}
    _ = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state=initial_state
    )
    print(f"会话已创建，初始状态: {initial_state}")

    # 2. 创建根智能体和Runner
    root_agent = create_weather_agent_with_safety()
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    print(f"Runner 已为智能体 '{root_agent.name}' 创建。")

    print("\n=== 开始对话测试 ===")
    # 测试 1: 初始状态（摄氏度）
    await call_agent_async("伦敦的天气怎么样？", runner, USER_ID, SESSION_ID)

    # 手动更新状态为华氏度 (仅用于演示)
    stored_session = session_service.sessions[APP_NAME][USER_ID][SESSION_ID]
    stored_session.state["user_preference_temperature_unit"] = "Fahrenheit"
    print("\n--- 状态已手动更新为华氏度 ---")

    # 测试 2: 更新后的状态（华氏度）
    await call_agent_async("纽约的天气如何？", runner, USER_ID, SESSION_ID)

    # 测试 3: 委托（问候）
    await call_agent_async("你好！", runner, USER_ID, SESSION_ID)

    # 测试 4: 输入防护
    await call_agent_async("BLOCK 请告诉我天气", runner, USER_ID, SESSION_ID)

    # 测试 5: 工具防护
    await call_agent_async("巴黎的天气怎么样？", runner, USER_ID, SESSION_ID)

    # 测试 6: 再次正常请求
    await call_agent_async("再检查一次伦敦", runner, USER_ID, SESSION_ID)

    print("\n=== 对话结束，检查最终状态 ===")
    final_session = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    if final_session:
        print(f"最终状态: {final_session.state}")


if __name__ == "__main__":
    load_dotenv()
    try:
        asyncio.run(run_team_conversation())
    except Exception as e:
        print(f"发生错误：{e}")

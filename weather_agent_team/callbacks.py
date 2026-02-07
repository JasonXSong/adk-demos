"""
回调模块：定义所有用于安全防护和自定义逻辑的回调函数。
"""

from typing import Optional, Dict, Any
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext


def block_keyword_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """检查最新用户消息中的 'BLOCK'。如果找到，则阻止 LLM 调用。"""
    agent_name = callback_context.agent_name
    print(f"--- 回调：block_keyword_guardrail 正在为智能体运行：{agent_name} ---")

    last_user_message_text = ""
    if llm_request.contents:
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts and content.parts[0].text:
                last_user_message_text = content.parts[0].text
                break

    print(f"--- 回调：正在检查最后一条用户消息：'{last_user_message_text[:100]}...' ---")

    keyword_to_block = "BLOCK"
    if keyword_to_block in last_user_message_text.upper():
        print(f"--- 回调：发现 '{keyword_to_block}'。正在阻止 LLM 调用！---")
        callback_context.state["guardrail_block_keyword_triggered"] = True
        print(f"--- 回调：设置状态 'guardrail_block_keyword_triggered': True ---")

        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=f"我无法处理此请求，因为它包含被阻止的关键字 '{keyword_to_block}'。")]
            )
        )
    else:
        print(f"--- 回调：未找到关键字。允许 {agent_name} 的 LLM 调用。---")
        return None


def block_paris_tool_guardrail(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """检查是否为 'Paris' 调用了 'get_weather_stateful'。如果是，则阻止工具执行。"""
    tool_name = tool.name
    agent_name = tool_context.agent_name
    print(f"--- 回调：block_paris_tool_guardrail 正在为智能体 '{agent_name}' 中的工具 '{tool_name}' 运行 ---")
    print(f"--- 回调：正在检查参数：{args} ---")

    target_tool_name = "get_weather_stateful"
    blocked_city = "paris"

    if tool_name == target_tool_name:
        city_argument = args.get("city", "")
        if city_argument and city_argument.lower() == blocked_city:
            print(f"--- 回调：检测到被阻止的城市 '{city_argument}'。正在阻止工具执行！---")
            tool_context.state["guardrail_tool_block_triggered"] = True
            print(f"--- 回调：设置状态 'guardrail_tool_block_triggered': True ---")
            return {
                "status": "error",
                "error_message": f"策略限制：目前通过工具防护已禁用针对 '{city_argument.capitalize()}' 的天气检查。"
            }
        else:
            print(f"--- 回调：城市 '{city_argument}' 允许用于工具 '{tool_name}'。---")
    else:
        print(f"--- 回调：工具 '{tool_name}' 不是目标工具。允许。---")

    print(f"--- 回调：允许工具 '{tool_name}' 继续。---")
    return None

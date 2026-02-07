from typing import Optional

from google.adk.tools.tool_context import ToolContext


def say_hello(name: Optional[str] = None) -> str:
    """
    提供简单的问候。如果提供了名字，将使用它。
    
    :param name: 要问候的人的名字。如果未提供，则默认为通用问候。
    :return: 友好的问候消息。
    """
    if name:
        greeting = f"你好，{name}！"
        print(f"--- 工具：say_hello 被调用，名字：{name} ---")
    else:
        greeting = "你好！" # 如果 name 为 None 或未明确传递，则使用默认问候
        print(f"--- 工具：say_hello 被调用，没有特定名字（name_arg_value：{name}）---")
    return greeting


def say_goodbye() -> str:
    """
    提供简单的告别消息以结束对话。
    """
    print(f"--- 工具：say_goodbye 被调用 ---")
    return "再见！祝你有美好的一天。"


def get_weather(city: str) -> dict:
    """
    获取指定城市的当前天气报告。
    
    :param city: 城市的英文名称（例如，"New York"、"London"、"Tokyo"）。
    :return: 包含天气信息的字典。
    """
    print(f"--- 工具：get_weather 被调用，城市：{city} ---") # 记录工具执行
    city_normalized = city.lower().replace(" ", "") # 基本标准化

    # 模拟天气数据
    mock_weather_db = {
        "newyork": {
            "status": "success",
            "report": "纽约的天气是晴朗的，温度为 25°C。"
        },
        "london": {
            "status": "success",
            "report": "伦敦多云，温度为 15°C。"
        },
        "tokyo": {
            "status": "success",
            "report": "东京有小雨，温度为 18°C。"
        }
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {
            "status": "error",
            "error_message": f"抱歉，我没有 '{city}' 的天气信息。"
        }


def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """
    检索指定城市的天气，根据会话状态转换温度单位。

    :param city: 城市的英文名称（例如，"New York"、"London"、"Tokyo"）。
    :param tool_context: 工具上下文对象，用于访问和修改状态。
    :return: 包含天气信息的字典。
    """
    print(f"--- 工具：get_weather_stateful 为 {city} 调用 ---")

    # --- 从状态读取偏好 ---
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius") # 默认为摄氏度
    print(f"--- 工具：读取状态 'user_preference_temperature_unit'：{preferred_unit} ---")

    city_normalized = city.lower().replace(" ", "")

    # 模拟天气数据（内部始终以摄氏度存储）
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # 根据状态偏好格式化温度
        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9/5) + 32 # 计算华氏度
            temp_unit = "°F"
        else: # 默认为摄氏度
            temp_value = temp_c
            temp_unit = "°C"

        report = f"{city.capitalize()} 的天气是 {condition}，温度为 {temp_value:.0f}{temp_unit}。"
        result = {"status": "success", "report": report}
        print(f"--- 工具：以 {preferred_unit} 生成报告。结果：{result} ---")

        # 写回状态的示例（此工具可选）
        tool_context.state["last_city_checked_stateful"] = city
        print(f"--- 工具：更新状态 'last_city_checked_stateful'：{city} ---")

        return result
    else:
        # 处理未找到城市的情况
        error_msg = f"抱歉，我没有 '{city}' 的天气信息。"
        print(f"--- 工具：未找到城市 '{city}'。---")
        return {"status": "error", "error_message": error_msg}

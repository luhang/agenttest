"""
OpenAI Agents SDK 入门 Demo
============================
演示三个核心概念：
  1. Agent        —— 带 instructions 的大模型角色
  2. @function_tool —— 让模型能调用你的 Python 函数
  3. Handoff      —— Agent 之间的任务转交

运行前先设置环境变量：
  Windows (PowerShell):  $env:OPENAI_API_KEY = "sk-..."
  Windows (Git Bash):    export OPENAI_API_KEY = "sk-..."
  macOS / Linux:         export OPENAI_API_KEY = "sk-..."

然后运行：
  python demo.py
"""

import asyncio

from agents import Agent, Runner, function_tool


# ---------------------------------------------------------------
# 1. 工具（Tool）：用装饰器把普通 Python 函数暴露给模型
#    模型会读取函数签名和 docstring 来决定何时调用它
# ---------------------------------------------------------------
@function_tool
def get_weather(city: str) -> str:
    """查询指定城市当前的天气。"""
    # Demo 里返回假数据；真实场景这里可以调天气 API
    fake_db = {
        "北京": "晴，18°C，西北风 3 级",
        "上海": "小雨，22°C，湿度 85%",
        "东京": "多云，15°C",
    }
    return fake_db.get(city, f"{city}：暂无数据（demo 只收录了北京/上海/东京）")


@function_tool
def convert_currency(amount: float, rate: float = 7.25) -> str:
    """把美元金额按汇率换算成人民币。"""
    return f"{amount:.2f} USD ≈ {amount * rate:.2f} CNY（汇率 {rate}）"


# ---------------------------------------------------------------
# 2. Agent：给模型一个角色和它可用的工具
# ---------------------------------------------------------------
weather_agent = Agent(
    name="天气助手",
    instructions=(
        "你是一个简洁的中文天气助手。"
        "用户问到天气时调用 get_weather 工具查询，再自然地回答。"
        "回答控制在两句话以内。"
    ),
    tools=[get_weather, convert_currency],
    model="gpt-4o-mini",
)


# ---------------------------------------------------------------
# 3. Handoff（转交）：一个 Agent 可以把对话转给更合适的 Agent
#    这里做一个"前台分流"：闲聊归闲聊员，天气问题转给天气助手
# ---------------------------------------------------------------
chitchat_agent = Agent(
    name="闲聊员",
    instructions="你是友好的闲聊伙伴，用中文轻松地回应，不超过两句话。",
    model="gpt-4o-mini",
)

triage_agent = Agent(
    name="前台",
    instructions="根据用户消息判断：天气相关就转给天气助手，其他闲聊转给闲聊员。",
    handoffs=[weather_agent, chitchat_agent],
    model="gpt-4o-mini",
)


async def main() -> None:
    print("=" * 60)
    print("Demo 1：单个 Agent + 工具调用")
    print("=" * 60)
    result = await Runner.run(weather_agent, "东京今天天气怎么样？适合穿什么？")
    print(f"回答：{result.final_output}\n")

    print("=" * 60)
    print("Demo 2：Handoff —— 前台自动转交")
    print("=" * 60)
    result = await Runner.run(triage_agent, "帮我查一下上海的天气")
    # 转交后，final_agent 会变成真正接手的那个 Agent
    print(f"最终由 [{result.final_agent.name}] 接手")
    print(f"回答：{result.final_output}\n")

    print("=" * 60)
    print("Demo 3：多轮对话（把上轮历史带回来）")
    print("=" * 60)
    result = await Runner.run(weather_agent, "100 美元能换多少人民币？")
    print(f"回答：{result.final_output}")
    # to_input_list() 把本轮对话转成历史，供下一轮继续
    history = result.to_input_list()
    result2 = await Runner.run(weather_agent, history + [{"role": "user", "content": "那 250 美元呢？"}])
    print(f"追问回答：{result2.final_output}")


if __name__ == "__main__":
    asyncio.run(main())

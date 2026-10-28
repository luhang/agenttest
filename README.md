# OpenAI Agents SDK Demo

最简入门示例，演示 SDK 的三个核心概念：

| 概念 | 在哪里 | 说明 |
|---|---|---|
| **Agent** | `weather_agent` / `triage_agent` | instructions + 模型 + 工具/转交的组合 |
| **Tool** | `get_weather` / `convert_currency` | `@function_tool` 装饰器把 Python 函数暴露给模型 |
| **Handoff** | `triage_agent.handoffs=[...]` | 前台 Agent 自动把任务转给更合适的 Agent |

## 运行

```bash
pip install -r requirements.txt

# 设置 Key（二选一）
export OPENAI_API_KEY="sk-..."          # Git Bash / macOS / Linux
$env:OPENAI_API_KEY = "sk-..."          # PowerShell

python demo.py
```

## 预期输出（示意）

```
Demo 1：单个 Agent + 工具调用
回答：东京今天多云，15°C，建议带件薄外套。

Demo 2：Handoff —— 前台自动转交
最终由 [天气助手] 接手
回答：上海现在小雨，22°C，出门记得带伞。

Demo 3：多轮对话（把上轮历史带回来）
回答：100.00 USD ≈ 725.00 CNY（汇率 7.25）
追问回答：250.00 USD ≈ 1812.50 CNY（汇率 7.25）
```

## 常用扩展方向

- **输出结构化**：`Runner.run(agent, input, output_type=PydanticModel)` 让结果直接是强类型对象
- **流式输出**：`Runner.run_streamed(...)` 返回增量 token
- **Guardrails**：给 Agent 挂输入/输出护栏（如拦截敏感内容）
- **Tracing**：运行后终端会打印 trace 链接，可在 OpenAI 平台可视化看到每一步工具调用与转交
- **其他模型**：兼容 OpenAIChatCompletionsModel 接入任意第三方模型

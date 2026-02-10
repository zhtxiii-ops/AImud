# 任务 5: OODA 循环自主智能体 (Task 5: OODA Loop Autonomous Agent)

本目录包含了一个基于 OODA（观察-调整-决策-行动）循环的自主智能体实现，用于通过 Socket 协议与服务器进行交互。

## 目录结构

*   **`config.py`**: 集中化配置文件。包含 Socket 连接地址、LLM API Key 及相关常量。
*   **`agent.py`**: 智能体主程序。实现了连接 Socket、接收数据、通过 LLM 分析决策、发送指令的完整循环。
    *   **目标管理**: 维护长期目标和短期目标，并根据交互动态更新。
    *   **知识库**: 使用 `knowledge_base.json` 持久化存储习得的知识，并包含信息熵检查机制。
    *   **日志**: 交互记录会保存在 `agent_interaction.log` 中。
*   **`run_agent.sh`**: **推荐启动方式**。后台运行智能体，自动处理日志重定向。
*   **`knowledge_base.json`**: 持久化知识库文件，存储高信息熵的知识点。
*   **`llm_client.py`**: 大模型客户端封装。负责构建 Prompt 并调用 DeepSeek API 获取决策。
*   **`task5.md`**: 原始任务说明文档。

## 如何运行

### 1. 确认配置
所有关键配置都集中在 `config.py` 中。您可以根据需要修改其中的 `TARGET_IP`、`TARGET_PORT` 或 `API_KEY`。

此外，该系统也支持通过环境变量进行覆盖：
- `AGENT_TARGET_IP`: 目标服务器 IP
- `AGENT_TARGET_PORT`: 目标服务器端口
- `DEEPSEEK_API_KEY`: 您的 API 密钥

### 2. 启动智能体 (推荐)
使用脚本在后台启动智能体：
```bash
./run_agent.sh
```
该脚本会将运行日志输出到 `agent_runtime.log`，交互日志输出到 `agent_interaction.log`。

或者手动前台运行：
```bash
python agent.py
```

### 3. 停止智能体
运行以下脚本停止所有后台运行的智能体进程：
```bash
./stop_agent.sh
```

### 4. 查看日志
智能体会实时追加写入到日志文件：
```bash
tail -f agent_interaction.log
```

## 核心特性

### 1. 目标导向 (Goal-Oriented)
智能体维护两个维度的目标：
*   **长期目标 (Long-term Goal)**: 如“探索服务器并理解其命令，寻找 Flag”。
*   **短期目标 (Short-term Goal)**: 如“成功登录服务器”。
智能体会在每一步交互中评估目标完成情况并动态调整。

### 2. 持久化与信息熵检查 (Entropy-Checked Knowledge Base)
*   **持久化**: 知识库保存为 `knowledge_base.json`，重启后不丢失。
*   **信息熵检查**: 引入二次 LLM 检查机制。在保存新知识前，会询问 LLM 该信息是否提供了真正的新价值（高信息熵）。只有通过检查的知识才会被写入，有效防止了重复和低价值信息的堆积。

## 工作原理

1.  **Observe (观察)**: 从 Socket 读取服务器返回的文本，并清除 ANSI 控制字符。
2.  **Orient (调整)**: 加载持久化知识库、读取历史交互、确认当前目标，组合成 System Prompt。
3.  **Decide (决策)**: 
    *   调用 LLM 分析当前状态。
    *   更新长期/短期目标。
    *   提取新知识（Candidate）。
    *   **Entropy Check**: 调用 LLM 判断新知识是否高熵。
    *   决定下一步 Payload。
4.  **Act (行动)**: 将 Payload 发送给服务器，更新历史记录，持久化保存高熵知识。

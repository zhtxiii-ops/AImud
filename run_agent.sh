
#!/bin/bash

# 定义日志文件
LOG_FILE="agent_runtime.log"

# 获取脚本所在目录
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 切换到脚本目录
cd "$DIR"

echo "[*] 正在启动 Agent..."

# 后台运行 agent.py
# -u: 禁用 python 的 stdout/stderr 缓冲
# 2>&1: 将 stderr 重定向到 stdout
# &: 后台运行
nohup python3 -u agent.py >> "$LOG_FILE" 2>&1 &

# 获取 PID
PID=$!

echo "[*] Agent 已在后台启动，PID: $PID"
echo "[*] 运行日志将写入: $DIR/$LOG_FILE"
echo "[*] 交互日志将写入: $DIR/agent_interaction.log"
echo "[*] 使用 'tail -f $LOG_FILE' 查看运行状态"

#!/bin/bash

# Find and kill agent.py processes
PIDS=$(pgrep -f "python.*agent.py")

if [ -z "$PIDS" ]; then
    echo "[*] 没有发现运行中的 agent.py 进程。"
else
    echo "[*] 正在停止以下进程: $PIDS"
    # shellcheck disable=SC2086
    kill $PIDS
    echo "[+] 所有 agent.py 进程已停止。"
fi

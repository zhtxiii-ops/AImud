import os

# Socket 连接配置
# 目标服务器 IP
TARGET_IP = os.environ.get("AGENT_TARGET_IP", "127.0.0.1")
# 目标服务器端口 (默认 MUD 端口 4000)
TARGET_PORT = int(os.environ.get("AGENT_TARGET_PORT", 4000))

# 智能体运行配置
# 历史记录最大保留轮数
MAX_HISTORY_ROUNDS = 10
# 交互日志文件路径
LOG_FILE = "agent_interaction.log"
# 知识库持久化文件路径
KB_FILE = "knowledge_base.json"

# LLM 配置
# DeepSeek API Key (优先从环境变量读取)
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "YOUR_API_KEY_HERE")
# API 基础 URL
BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
# 使用的大模型名称
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

# 颜色配置 (用于终端展示)
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"  # Client
    YELLOW = "\033[93m" # Short-term Goal
    BLUE = "\033[94m"   # Long-term Goal
    MAGENTA = "\033[95m" # KB Update
    CYAN = "\033[96m"   # Analysis
    WHITE = "\033[97m"

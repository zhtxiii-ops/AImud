
import socket
import time
import json
import sys
import os
from llm_client import LLMClient

# 配置
TARGET_IP = "127.0.0.1"
TARGET_PORT = 4000
MAX_HISTORY_ROUNDS = 10
LOG_FILE = "agent_interaction.log"
KB_FILE = "knowledge_base.json"

class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"  # Client
    YELLOW = "\033[93m" # Short-term Goal
    BLUE = "\033[94m"   # Long-term Goal
    MAGENTA = "\033[95m" # KB Update
    CYAN = "\033[96m"   # Analysis
    WHITE = "\033[97m"

def log_colored(tag, message, color=None):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    if color:
        formatted_msg = f"[{timestamp}] {color}[{tag}] {message}{Colors.RESET}"
    else:
        formatted_msg = f"[{timestamp}] [{tag}] {message}"
    
    # 同时打印到控制台 (带颜色)
    print(formatted_msg)
    
    # 写入文件 (保留颜色代码，以便 tail -f 显示颜色)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted_msg + "\n")

def load_kb():
    if not os.path.exists(KB_FILE):
        return []
    try:
        with open(KB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_kb(current_kb):
    with open(KB_FILE, "w", encoding="utf-8") as f:
        json.dump(current_kb, f, ensure_ascii=False, indent=2)

def call_llm_with_retry(llm, system_prompt, user_content, json_mode=True, validator=None):
    """
    循环调用 LLM 直到成功为止。
    validator: 一个函数，接受 LLM 返回及，如果验证通过返回 True，否则返回 False。
               如果不提供 validator，只要 LLM 返回且未抛出异常即视为成功。
    """
    while True:
        try:
            result = llm.query(system_prompt, user_content, json_mode=json_mode)
            
            if validator:
                if validator(result):
                    return result
                else:
                    log_colored("系统", "LLM 返回结果未通过验证，正在重试...", Colors.RED)
                    time.sleep(2)
                    continue
            return result

        except Exception as e:
            log_colored("系统", f"LLM 调用失败: {e}。2秒后重试...", Colors.RED)
            time.sleep(2)

def check_entropy(llm, current_kb, new_knowledge):
    """
    使用 LLM 检查新知识是否增加了信息熵（即是否提供了真正的新信息）。
    """
    if not new_knowledge:
        return False
        
    # 如果完全一模一样的字符串，直接返回 False (节省 token)
    if new_knowledge in current_kb:
        return False

    kb_str = "\n".join([f"- {k}" for k in current_kb]) if current_kb else "暂无。"
    
    prompt = f"""
    你是一个知识库管理员。你的任务是判断“新知识”是否为现有的“知识库”增加了有价值的信息。
    
    现有知识库:
    {kb_str}
    
    建议添加的新知识:
    "{new_knowledge}"
    
    判断标准:
    1. 如果新知识是现有知识的**完全重复**或**毫无意义的废话**，请回答 NO。
    2. 如果新知识提供了以下任何一种信息，请回答 YES：
       - 新的地点描述、物品详情、NPC信息。
       - 命令的成功执行结果或特定的错误反馈。
       - 剧情线索或任务信息。
       - 任何现有知识库中不存在的有效细节。
    3. 我们希望知识库尽可能详尽，不要担心信息过于琐碎，只要它是新的且真实的。
    
    请严格输出如下 JSON 格式：
    {{
        "decision": "YES" 或 "NO"
    }}
    """
    
    def entropy_validator(res):
        if not isinstance(res, dict): return False
        decision = res.get("decision", "").strip().upper()
        return decision in ["YES", "NO"]

    # 使用 retry 包装调用
    result = call_llm_with_retry(llm, prompt, "请判断。", json_mode=True, validator=entropy_validator)
    
    decision = result.get("decision", "NO").strip().upper()
    
    if "YES" in decision:
        print(f"{Colors.MAGENTA}[Entropy Check] LLM 判定: YES{Colors.RESET}")
        return True
    else:
        print(f"{Colors.YELLOW}[Entropy Check] LLM 判定: NO{Colors.RESET}")
        return False

def main():
    log_colored("系统", f"正在启动自主智能体，目标：{TARGET_IP}:{TARGET_PORT}", Colors.WHITE)
    
    # 初始化 LLM 客户端
    llm = LLMClient()
    
    # 状态
    history = []
    long_term_goal = "探索服务器并理解含义，根据服务器的特点确定一个长期目标。"
    short_term_goal = "成功登录服务器"
    
    while True: # 自动重连循环
        s = None
        try:
            # 连接
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5.0)
                s.connect((TARGET_IP, TARGET_PORT))
                log_colored("系统", f"已连接到 {TARGET_IP}:{TARGET_PORT}", Colors.WHITE)
            except Exception as e:
                log_colored("系统", f"连接失败：{e}。5秒后重试...", Colors.RED)
                time.sleep(5)
                continue

            # 交互循环
            while True:
                # --- 1. 观察 (接收) ---
                try:
                    data = s.recv(4096)
                    if not data:
                        log_colored("系统", "服务器关闭了连接", Colors.RED)
                        break
                    server_output = data.decode('utf-8', errors='ignore').strip()
                    # Server output keeps its own colors if any, we don't add wrapper color
                    log_colored("服务器", server_output) 
                except socket.timeout:
                    server_output = "<超时 - 无响应>"
                    log_colored("服务器", server_output)
                except (ConnectionResetError, BrokenPipeError) as e:
                    log_colored("系统", f"连接中断：{e}", Colors.RED)
                    break # 跳出内层循环，触发重连
                except Exception as e:
                    log_colored("系统", f"Socket 错误：{e}", Colors.RED)
                    break

                # 清理服务器输出中的控制字符（保留换行符）
                import re
                # 移除 ANSI 转义序列
                server_output_clean = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', server_output)
                # 移除除了 \n 和可打印字符以外的控制字符
                server_output_clean = "".join(ch for ch in server_output_clean if ch == '\n' or (ord(ch) >= 32 and ord(ch) != 127))
                
                # --- 2. 分析与规划 (LLM) ---
                
                # 加载最新的知识库
                current_kb = load_kb()
                
                # 构建知识库字符串
                kb_str = "\n".join([f"- {k}" for k in current_kb]) if current_kb else "暂无。"
                
                # 构建最近历史记录
                recent_history = history[-MAX_HISTORY_ROUNDS:]
                history_str = "\n".join(recent_history)
                
                system_prompt = f"""\
你是一个网络协议安全专家和自主智能体。
你的长期目标 (Long-term Goal): {long_term_goal}
你的短期目标 (Short-term Goal): {short_term_goal}

当前知识库 (Current Knowledge Base，已持久化保存):
{kb_str}

交互历史 (Interaction History, Client -> Server):
{history_str}

服务器的最后输出是："{server_output_clean}"

你的任务：
1. 分析服务器的响应。
2. 推断关于协议的新知识（状态转移、命令、错误）。
3. 评估当前目标是否完成，或者基于目前所有信息是否需要修改目标。注意：长期目标不宜频繁修改，请慎重制定。
4. 如果反复尝试发现目前的短期目标无法完成，请重新制定一个不同的短期目标。
5. 围绕你的长期目标和短期目标决定下一步发送的 Payload。

*** 知识库更新原则 (Information Entropy CHECK) ***
- 用于提议新知识。
- 你的目标是尽可能详尽地记录世界。
- 请积极记录：
    1. 新的信息。
    4. 成功的命令及其产生的效果。
    5. 任何新发现的机制或规则。
- 仅当信息完全重复（此时此刻已在KB中）或完全无意义时，才留空。
- [重要] 任何验证过的用户名和密码组合都被视为极高熵的知识，必须保存到知识库中 (格式: 用户名: <username>, 密码: <password>)。

严格以 JSON 格式输出：
{{
    "analysis": "你的推理过程...",
    "new_knowledge": "提议的新知识，否则留空",
    "long_term_goal": "更新后的长期目标",
    "short_term_goal": "更新后的短期目标",
    "next_payload": "下一步要发送的具体字符串"
}}
                """
                
                user_msg = f"服务器说：{server_output_clean}。你的下一步行动是什么？"
                
                print("[*] 思考中...") # 保持控制台提示，不计入日志
                
                def main_logic_validator(res):
                    # 简单验证：必须是字典，且包含 analysis 和 next_payload
                    return isinstance(res, dict) and "analysis" in res

                decision = call_llm_with_retry(llm, system_prompt, user_msg, json_mode=True, validator=main_logic_validator)
                
                # 解析决策
                analysis = decision.get("analysis", "无分析")
                new_kb = decision.get("new_knowledge", "")
                new_long_goal = decision.get("long_term_goal", long_term_goal)
                new_short_goal = decision.get("short_term_goal", short_term_goal)
                payload = decision.get("next_payload", "")
                
                log_colored("大脑", f"分析：{analysis}", Colors.CYAN)
                
                # 更新目标
                if new_long_goal != long_term_goal:
                    log_colored("大脑", f"长期目标更新：{long_term_goal} -> {new_long_goal}", Colors.BLUE)
                    long_term_goal = new_long_goal
                    
                if new_short_goal != short_term_goal:
                    log_colored("大脑", f"短期目标更新：{short_term_goal} -> {new_short_goal}", Colors.YELLOW)
                    short_term_goal = new_short_goal
    
                # --- 3. 更新状态 ---
                if new_kb:
                    # 使用 LLM 进行二次熵检查
                    if check_entropy(llm, current_kb, new_kb):
                        log_colored("大脑", f"习得并保存（LLM确认高熵）：{new_kb}", Colors.MAGENTA)
                        current_kb.append(new_kb)
                        save_kb(current_kb)
                    else:
                         # 低熵信息可以不记录到日志以减少噪音，或者用灰色/白色记录
                         log_colored("大脑", f"知识被LLM判定为冗余（低熵）：{new_kb}", Colors.RESET)
    
                # --- 4. 行动 (发送) ---
                if payload:
                    log_colored("客户端", f"发送：{payload}", Colors.GREEN)
                    try:
                        s.sendall((payload + "\n").encode('utf-8'))
                        # 更新历史
                        history.append(f"In: {payload} | Out: {server_output_clean[:50]}...")
                    except (ConnectionResetError, BrokenPipeError) as e:
                        log_colored("系统", f"发送错误（连接中断）：{e}", Colors.RED)
                        break # 触发重连
                    except Exception as e:
                        log_colored("系统", f"发送错误：{e}", Colors.RED)
                        break
                else:
                    log_colored("大脑", "决定不发送任何内容。", Colors.CYAN)
                
                # 避免过快请求服务器
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n[!] 用户中断。")
            break
        except Exception as e:
             print(f"[!] 发生未捕获异常：{e}。5秒后重启...")
             log_to_file(f"发生未捕获异常：{e}。5秒后重启...")
             time.sleep(5)
        finally:
            if s:
                s.close()
                print("[*] 已断开连接。")

if __name__ == "__main__":
    main()

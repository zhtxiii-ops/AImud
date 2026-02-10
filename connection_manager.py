import socket
import re
import time
import config
from config import Colors

class SocketClient:
    def __init__(self, ip=config.TARGET_IP, port=config.TARGET_PORT):
        self.ip = ip
        self.port = port
        self.socket = None
        self.connected = False

    def connect(self):
        """尝试连接到服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((self.ip, self.port))
            self.connected = True
            print(f"{Colors.WHITE}[系统] 已连接到 {self.ip}:{self.port}{Colors.RESET}")
            return True
        except Exception as e:
            print(f"{Colors.RED}[系统] 连接失败：{e}{Colors.RESET}")
            self.connected = False
            return False

    def disconnect(self):
        """断开连接"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.socket = None
        self.connected = False
        print(f"{Colors.WHITE}[系统] 已断开连接{Colors.RESET}")

    def send(self, data):
        """发送数据，自动添加换行符"""
        if not self.connected or not self.socket:
            return False
        try:
            self.socket.sendall((data + "\n").encode('utf-8'))
            return True
        except (ConnectionResetError, BrokenPipeError) as e:
            print(f"{Colors.RED}[系统] 发送错误（连接中断）：{e}{Colors.RESET}")
            self.disconnect()
            return False
        except Exception as e:
            print(f"{Colors.RED}[系统] 发送错误：{e}{Colors.RESET}")
            self.disconnect()
            return False

    def receive(self, buffer_size=4096):
        """接收数据并进行预处理（清洗 ANSI 字符）"""
        if not self.connected or not self.socket:
            return None
        
        try:
            data = self.socket.recv(buffer_size)
            if not data:
                print(f"{Colors.RED}[系统] 服务器关闭了连接{Colors.RESET}")
                self.disconnect()
                return None
            
            raw_output = data.decode('utf-8', errors='ignore').strip()
            return raw_output

        except socket.timeout:
            return "<超时 - 无响应>"
        except (ConnectionResetError, BrokenPipeError) as e:
            print(f"{Colors.RED}[系统] 连接中断：{e}{Colors.RESET}")
            self.disconnect()
            return None
        except Exception as e:
            print(f"{Colors.RED}[系统] Socket 错误：{e}{Colors.RESET}")
            self.disconnect()
            return None

    def clean_ansi(self, text):
        """清理 ANSI 转义序列和不可打印字符"""
        # 移除 ANSI 转义序列
        text_clean = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)
        # 移除除了 \n 和可打印字符以外的控制字符
        text_clean = "".join(ch for ch in text_clean if ch == '\n' or (ord(ch) >= 32 and ord(ch) != 127))
        return text_clean

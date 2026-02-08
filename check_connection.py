
import socket
import time
import sys

HOST = '127.0.0.1'
PORT = 4000

def test_connection():
    print(f"[*] 正在连接 {HOST}:{PORT}...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((HOST, PORT))
        print("[*] 连接成功。")
    except Exception as e:
        print(f"[!] 连接失败: {e}")
        return

    # 测试交互序列：发送名字 -> 发送密码 -> 发送命令
    # 注意：必须添加换行符 \n，否则服务器可能不会处理命令
    inputs = ["start_test", "123456", "look", "quit"]
    
    try:
        # 接收欢迎信息
        print("[*] 等待服务器欢迎信息...")
        try:
            data = s.recv(4096)
            print(f"[服务器]:\n{data.decode('utf-8', errors='ignore')}")
        except socket.timeout:
            print("[!] 接收欢迎信息超时")

        for i, cmd in enumerate(inputs):
            print(f"\n[*] [测试步 {i+1}] 发送: {cmd}")
            try:
                # 发送带换行符的命令
                s.sendall((cmd + "\n").encode('utf-8'))
                
                # 接收响应
                time.sleep(1) # 给服务器一点处理时间
                data = s.recv(4096)
                if not data:
                    print("[!] 服务器关闭了连接")
                    break
                print(f"[服务器]: {data.decode('utf-8', errors='ignore').strip()}")
                
            except socket.timeout:
                print("[!] 等待响应超时 (Timeout)")
            except Exception as e:
                print(f"[!] 错误: {e}")
                break
                
    except Exception as e:
        print(f"[!] 交互错误: {e}")
    finally:
        s.close()
        print("[*] 连接已关闭。")

if __name__ == "__main__":
    test_connection()

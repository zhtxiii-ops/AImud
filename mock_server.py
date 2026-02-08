
import socket
import threading
import time

HOST = '127.0.0.1'
PORT = 4000

def handle_client(conn, addr):
    print(f"[SERVER] 来自 {addr} 的新连接")
    try:
        conn.sendall("欢迎来到 AlphaMUD。请输入ID：\n".encode('utf-8'))
        
        # 状态: 0=ID, 1=密码, 2=游戏
        state = 0
        
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            text = data.decode('utf-8').strip()
            print(f"[SERVER] 收到来自 {addr} 的消息: {text}")
            
            if state == 0:
                conn.sendall("ID已接受。请输入密码：\n".encode('utf-8'))
                state = 1
            elif state == 1:
                if text:
                    conn.sendall("欢迎来到这个世界！HP:100/100 >".encode('utf-8'))
                    state = 2
                else:
                    conn.sendall("密码不能为空。\n".encode('utf-8'))
            elif state == 2:
                if text == "help":
                    conn.sendall("指令：look, go, help, quit\nHP:100/100 >".encode('utf-8'))
                elif text == "look":
                    conn.sendall("你看到一个黑暗的房间。北边有一扇门。\nHP:100/100 >".encode('utf-8'))
                elif text.startswith("go"):
                    conn.sendall(f"你前往 {text[3:]}。那里很危险。\nHP:90/100 >".encode('utf-8'))
                elif text == "quit":
                    conn.sendall("再见。\n".encode('utf-8'))
                    break
                else:
                    conn.sendall(f"未知指令：{text}\nHP:100/100 >".encode('utf-8'))
                    
    except Exception as e:
        print(f"[SERVER] 错误: {e}")
    finally:
        conn.close()
        print(f"[SERVER] 连接已关闭 {addr}")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[SERVER] 正在监听 {HOST}:{PORT}")
    
    try:
        while True:
            conn, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.start()
    except KeyboardInterrupt:
        print("\n[SERVER] 正在停止...")
    finally:
        server.close()

if __name__ == "__main__":
    main()

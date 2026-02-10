import os
import json
from openai import OpenAI
import config

# 从统一配置文件读取配置
API_KEY = config.API_KEY
BASE_URL = config.BASE_URL
MODEL = config.MODEL

class LLMClient:
    def __init__(self, api_key=None, base_url=None, model=None):
        self.api_key = api_key or API_KEY
        self.base_url = base_url or BASE_URL
        self.model = model or MODEL
        
        # 初始化 OpenAI 客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
    def query(self, system_prompt, user_content, json_mode=True):
        """
        使用 OpenAI SDK 调用 LLM。
        """
        try:
            # 构造参数
            kwargs = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                "stream": False
            }
            
            # 如果启用 JSON 模式
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            # 发送请求
            response = self.client.chat.completions.create(**kwargs)
            
            #以此获取内容
            content = response.choices[0].message.content
            
            # 解析 JSON 内容 (如果 json_mode=True，通常返回的就是 JSON 字符串)
            # 即使 json_mode=False，为了兼容性，我们也尝试解析，或者直接返回
            if json_mode:
                return json.loads(content)
            else:
                 # 如果不是 JSON 模式，尝试解析，失败则返回原始内容的封装结构（虽然 agent.py 目前看似只用 JSON）
                 # 但为了兼容可能得非 JSON 调用，我们还是尝试 load
                 try:
                     return json.loads(content)
                 except json.JSONDecodeError:
                     return content

        except Exception as e:
            print(f"[LLM] OpenAI SDK 调用出错：{e}")
            raise e

if __name__ == "__main__":
    # 测试客户端
    client = LLMClient()
    print("正在测试 LLM 客户端 (OpenAI SDK)...")
    try:
        resp = client.query("你是一个乐于助人的助手。请输出 JSON。", "用 JSON 格式说你好，使用 'message' 键。", json_mode=True)
        print(resp)
    except Exception as e:
        print(f"测试失败: {e}")

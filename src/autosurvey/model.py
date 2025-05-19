import time
import requests
import json
from tqdm import tqdm
import threading

class APIModel:

    def __init__(self, model, api_key, api_url) -> None:
        self.__api_key = api_key
        self.__api_url = api_url
        self.model = model
        
    def __req(self, text, temperature, max_try = 5):
        url = f"{self.__api_url}"
        pay_load_dict = {
            "model": f"{self.model}",
            "messages": [{
                "role": "user",
                "content": f"{text}"
            }],
            "temperature": temperature
        }
        payload = json.dumps(pay_load_dict)
        headers = {
            'Authorization': f'Bearer {self.__api_key}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            
            # 打印更详细的响应信息，包括状态码和错误信息
            print(f"状态码: {response.status_code}")
            
            # 尝试解析JSON响应
            try:
                response_json = response.json()
                print(f"响应内容: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
                
                # 检查错误信息
                if response.status_code != 200:
                    error_message = response_json.get('error', {})
                    if isinstance(error_message, dict):
                        print(f"错误类型: {error_message.get('type', '未知')}")
                        print(f"错误消息: {error_message.get('message', '未知')}")
                        print(f"错误代码: {error_message.get('code', '未知')}")
                    else:
                        print(f"错误信息: {error_message}")
                
                if response.status_code == 200:
                    return response_json['choices'][0]['message']['content']
                else:
                    raise Exception(f"API请求失败，状态码：{response.status_code}")
            
            except json.JSONDecodeError:
                print(f"无法解析JSON响应: {response.text}")
                raise Exception("响应不是有效的JSON格式")
                
        except Exception as e:
            print(f"发生异常: {str(e)}")
            
            # 重试逻辑
            for attempt in range(max_try):
                try:
                    print(f"第{attempt+1}次重试...")
                    response = requests.request("POST", url, headers=headers, data=payload)
                    
                    if response.status_code == 200:
                        return response.json()['choices'][0]['message']['content']
                    else:
                        print(f"重试失败，状态码: {response.status_code}")
                except Exception as retry_error:
                    print(f"重试时发生异常: {str(retry_error)}")
                
                time.sleep(0.2 * (attempt + 1))  # 指数退避策略
            
            return f"请求失败，所有重试均未成功。最后一个错误: {str(e)}"
    
    def chat(self, text, temperature=1):
        response = self.__req(text, temperature=temperature, max_try=5)
        return response

    def __chat(self, text, temperature, res_l, idx):
        
        response = self.__req(text, temperature=temperature)
        res_l[idx] = response
        return response
        
    def batch_chat(self, text_batch, temperature=0):
        max_threads=15 # limit max concurrent threads using model API
        res_l = ['No response'] * len(text_batch)
        thread_l = []
        for i, text in zip(range(len(text_batch)), text_batch):
            thread = threading.Thread(target=self.__chat, args=(text, temperature, res_l, i))
            thread_l.append(thread)
            thread.start()
            while len(thread_l) >= max_threads: 
                for t in thread_l:
                    if not t .is_alive():
                        thread_l.remove(t)
                time.sleep(0.3) # Short delay to avoid busy-waiting

        for thread in tqdm(thread_l):
            thread.join()
        return res_l

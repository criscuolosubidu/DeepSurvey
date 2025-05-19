import os
from typing import List
import threading
import tiktoken
from tqdm import trange
import time
import requests
import random
import json
from langchain_community.document_loaders import PyPDFLoader

class tokenCounter():

    def __init__(self) -> None:
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.model_price = {}
        
    def num_tokens_from_string(self, string) -> int:
        if isinstance(string, str):
            return len(self.encoding.encode(string))
        else:
            # 如果不是字符串，尝试转换为字符串
            try:
                string_str = str(string)
                return len(self.encoding.encode(string_str))
            except Exception as e:
                print(f"警告：无法计算非字符串对象的token数量: {type(string)}")
                return 0

    def num_tokens_from_list_string(self, list_of_string:List[str]) -> int:
        num = 0
        for s in list_of_string:
            if isinstance(s, str):
                num += len(self.encoding.encode(s))
            else:
                # 如果不是字符串，尝试转换为字符串
                try:
                    s_str = str(s)
                    num += len(self.encoding.encode(s_str))
                except Exception as e:
                    print(f"警告：无法计算非字符串对象的token数量: {type(s)}")
        return num
    
    def compute_price(self, input_tokens, output_tokens, model):
        return (input_tokens/1000) * self.model_price[model][0] + (output_tokens/1000) * self.model_price[model][1]

    def text_truncation(self,text, max_len = 1000):
        encoded_id = self.encoding.encode(text, disallowed_special=())
        return self.encoding.decode(encoded_id[:min(max_len,len(encoded_id))])

def load_pdf(file, max_len = 1000):
    loader = PyPDFLoader(file)
    pages = loader.load_and_split()
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    text = ''.join([p.page_content for p in pages])
    return encoding.decode(encoding.encode(text)[:max_len])
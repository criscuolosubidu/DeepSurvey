from typing import List, Dict
from gevent.lock import Semaphore
from .local import LocalRequest
from .openai import OpenAIRequest
from .google import GoogleRequest

import logging
logger = logging.getLogger(__name__)



class RequestWrapper:
    _connection_semaphore = {}
    _calls_count = 0 # 用来统计api的调用次数
    _token_usage_history = [] # 用来统计每次调用时使用的token数

    def __init__(self, model="gemini-2.0-flash-thinking-exp-01-21", infer_type="OpenAI", connection=20, port=None):
        if not model:
            model = "gemini-2.0-flash-thinking-exp-01-21"
        
        self.request_pool = None
        self.model = model
        self._connection_semaphore[model] = Semaphore(connection)

        if infer_type == "OpenAI":
            self.request_pool = OpenAIRequest(model=model)
        elif infer_type == "Google":
            self.request_pool = GoogleRequest(model=model)  
        elif infer_type == "local":
            self.request_pool = LocalRequest(port=port)
        else:
            raise ValueError(
                f"Invalid infer_type: {infer_type}, should be OpenAI or local"
            )

    def completion(self, message, **kwargs):
        if isinstance(message, str):
            message = [{"role": "user", "content": message}]
        elif isinstance(message, List):
            if not all(
                isinstance(m, Dict)
                and "role" in m
                and "content" in m
                and isinstance(m["role"], str)
                and isinstance(m["content"], str)
                for m in message
            ):
                raise ValueError(
                    "message should be a List[Dict['role':str, 'content':str]]"
                )
                
        if self.model in self._connection_semaphore:
            with self._connection_semaphore[self.model]:
                logger.debug(f"Acquired semaphore for {self.model} (remain={self._connection_semaphore[self.model].counter})")
                result, token_usage = self.request_pool.completion(message, **kwargs)
        else:
            result, token_usage = self.request_pool.completion(message, **kwargs)
            
        self._calls_count += 1
        self._token_usage_history.append(token_usage)
            
        logger.debug(f"Requesting completion received")
        if not result:
            raise ValueError(
                f"Requesting completion failed, return with empty result, message length: {len(str(message))}"
            )
        return result

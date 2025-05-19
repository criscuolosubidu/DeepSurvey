from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

import arxiv
from src.utils.logger import SearchLogger
from rag.config import ArxivConfig, GoogleScholarConfig, ConfigFactory, SearchEngineType
import requests
import json
import time


@dataclass
class SearchResult:
    """搜索结果的数据类"""
    title: str
    url: str
    snippet: str
    source: str
    metadata: Dict[str, Any] = None


class SearchEngine(ABC):
    
    @abstractmethod
    def search(self, query: str, **kwargs) -> List[SearchResult]:
        pass


class AcademicSearchStrategy(ABC):
    
    @abstractmethod
    def search_papers(self, query: str, **kwargs) -> List[SearchResult]:
        pass


class GeneralSearchStrategy(ABC):
    
    @abstractmethod
    def search_web(self, query: str, **kwargs) -> List[SearchResult]:
        pass


class ArxivSearchEngine(SearchEngine, AcademicSearchStrategy):
    
    def __init__(
            self, 
            config: ArxivConfig = None, 
            api_key: Optional[str] = None, 
            max_results: Optional[int] = None
        ):
        self.config = config or ConfigFactory.create_config(SearchEngineType.ARXIV.value)
        if api_key:
            self.config.api_key = api_key
        if max_results:
            self.config.max_results = max_results
        self.logger = SearchLogger("arxiv_engine")
    
    def search(self, query: str, **kwargs) -> List[SearchResult]:
        self.logger.info("开始Arxiv搜索", query=query, **kwargs)
        return self.search_papers(query, **kwargs)
    
    def search_papers(self, query: str, **kwargs) -> List[SearchResult]:
        # 创建arxiv client
        client = arxiv.Client()

        max_results = kwargs.get('max_results', self.config.max_results)
        sort_by = kwargs.get('sort_by', self.config.sort_by)

        # 完成 max_results 和 sort_by 的类型检查
        # 检查 max_results 类型
        if not isinstance(max_results, int) or max_results <= 0:
            error_msg = f"max_results必须是正整数，当前值: {max_results}, 类型: {type(max_results).__name__}"
            self.logger.error(error_msg)
            raise TypeError(error_msg)
        
        if max_results > 10:
            self.logger.warning(f"max_results超过最大限制，已自动调整为10，原值: {max_results}")
            max_results = 10
            
        # 检查 sort_by 类型
        if not sort_by: # 因为默认是没有排序规则的，所以这里需要加上一个arXiv的排序规则
            sort_by = arxiv.SortCriterion.Relevance

        if not isinstance(sort_by, arxiv.SortCriterion):
            # 尝试将字符串转换为SortCriterion
            if isinstance(sort_by, str):
                try:
                    # 检查是否为有效的SortCriterion值
                    if sort_by in [sc.value for sc in arxiv.SortCriterion]:
                        # 将字符串值转换为枚举
                        for sc in arxiv.SortCriterion:
                            if sc.value == sort_by:
                                sort_by = sc
                                self.logger.debug(f"字符串sort_by已转换为枚举", original=sort_by, converted=sc)
                                break
                    else:
                        error_msg = f"无效的sort_by值: {sort_by}"
                        self.logger.error(error_msg)
                        raise ValueError(error_msg)
                except Exception as e:
                    error_msg = f"无法将sort_by转换为SortCriterion: {e}"
                    self.logger.error(error_msg)
                    raise TypeError(error_msg)
            else:
                error_msg = f"sort_by必须是arxiv.SortCriterion类型或有效的字符串值，当前值: {sort_by}, 类型: {type(sort_by).__name__}"
                self.logger.error(error_msg)
                raise TypeError(error_msg)
        
        # 构建arXiv API请求
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_by,
        )
        
        self.logger.debug("执行arXiv搜索", query=query, max_results=max_results, sort_by=sort_by)
        
        try:
            results = []
            for result in client.results(search):
                search_result = SearchResult(
                    title=result.title,
                    url=result.entry_id,
                    snippet=result.summary,
                    source="arXiv",
                    metadata={
                        "authors": [author.name for author in result.authors],
                        "published": str(result.published),
                        "categories": result.categories
                    }
                )
                results.append(search_result)
            
            self.logger.info(f"arXiv搜索完成", found_results=len(results))
            return results
        except Exception as e:
            self.logger.error(f"arXiv搜索出错", error=str(e), query=query)
            return []


class GoogleScholarSearchEngine(SearchEngine, AcademicSearchStrategy):
    """Google Scholar搜索引擎实现"""
    
    def __init__(
            self, 
            config: GoogleScholarConfig = None, 
            api_key: str = None, 
            max_results: Optional[int] = None
        ):
        self.config = config or ConfigFactory.create_config(SearchEngineType.GOOGLE_SCHOLAR.value)
        if api_key:
            self.config.api_key = api_key
        if max_results:
            self.config.max_results = max_results
        self.logger = SearchLogger("google_scholar_engine")
    
    def search(self, query: str, **kwargs) -> List[SearchResult]:
        """实现基类的搜索方法，调用学术搜索策略"""
        self.logger.info("开始Google Scholar搜索", query=query, **kwargs)
        return self.search_papers(query, **kwargs)
    
    def search_papers(self, query: str, **kwargs) -> List[SearchResult]:
        """实现Google Scholar搜索，支持分页获取多个结果"""
        max_results = kwargs.get('max_results', self.config.max_results)
        timeout = kwargs.get('timeout', self.config.timeout)
        api_key = kwargs.get('api_key', self.config.api_key)
        
        if not api_key:
            error_msg = "缺少Google Scholar API Key"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
              
        url = self.config.base_url
        base_payload = {
            "q": query,
            "hl": self.config.hl,
            "as_sdt": self.config.as_sdt,
            "as_vis": self.config.as_vis
        }
        
        # 添加其他可选参数
        for key, value in kwargs.items():
            if key not in ['max_results', 'timeout', 'api_key', 'page']:
                base_payload[key] = value
        
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        
        self.logger.debug("准备执行Google Scholar分页搜索", query=query, max_results=max_results)
        
        all_results = []
        current_page = 1
        results_per_page = 10  # Google Scholar API通常每页返回10条结果
        
        # 计算需要请求的最大的页数
        max_pages = (max_results + results_per_page - 1) // results_per_page
        
        try:
            while len(all_results) < max_results and current_page <= max_pages:
                payload = base_payload.copy()
                payload["page"] = current_page
                
                self.logger.debug(f"请求第{current_page}页搜索结果", payload=payload)
                
                response = requests.request(
                    "POST", 
                    url, 
                    headers=headers, 
                    data=json.dumps(payload),
                    timeout=timeout
                )
                response.raise_for_status()
                response_data = response.json()
                
                papers = response_data.get('organic', [])
                
                # 如果返回的论文为空，说明没有更多结果了
                if not papers:
                    self.logger.debug(f"第{current_page}页无结果，停止请求")
                    break
                
                # 处理搜索得到的结果
                for paper in papers:
                    metadata = {
                        "year": paper.get("year"),
                        "citedBy": paper.get("citedBy")
                    }
                    
                    if "pdfUrl" in paper:
                        metadata["pdfUrl"] = paper.get("pdfUrl")
                    
                    if "id" in paper:
                        metadata["id"] = paper.get("id")
                    
                    if "publicationInfo" in paper:
                        metadata["publicationInfo"] = paper.get("publicationInfo")
                    
                    search_result = SearchResult(
                        title=paper.get("title", ""),
                        url=paper.get("link", ""),
                        snippet=paper.get("snippet", ""),
                        source="Google Scholar",
                        metadata=metadata
                    )
                    all_results.append(search_result)
                    
                    # 如果已经达到了请求的结果数量，就停止处理
                    if len(all_results) >= max_results:
                        break
                
                # 请求下一页
                current_page += 1
                
                # 添加请求间隔，避免触发API限制
                if current_page <= max_pages and len(all_results) < max_results:
                    time.sleep(1)  # 每次请求间隔1秒
            
            self.logger.info("Google Scholar搜索完成", 
                             found_results=len(all_results), 
                             requested_pages=current_page-1,
                             max_results=max_results)
            
            # 确保结果数量不超过max_results
            return all_results[:max_results]
        
        except requests.exceptions.Timeout:
            self.logger.error("Google Scholar搜索超时", timeout=timeout, query=query)
            return all_results if all_results else []
            
        except requests.exceptions.HTTPError as e:
            status_code = getattr(e.response, 'status_code', None)
            self.logger.error(f"Google Scholar HTTP错误", 
                             error=str(e), 
                             status_code=status_code, 
                             query=query,
                             current_page=current_page)
            return all_results if all_results else []
            
        except Exception as e:
            self.logger.error(f"Google Scholar搜索出错", 
                             error=str(e), 
                             query=query,
                             current_page=current_page)
            return all_results if all_results else []


class SearchEngineFactory:
    """搜索引擎工厂，负责创建和管理搜索引擎实例"""
    
    @staticmethod
    def create_engine(engine_type: str, **engine_config) -> SearchEngine:
        """
        创建搜索引擎实例
        
        Args:
            engine_type: 搜索引擎类型('arxiv', 'google_scholar'等)
            **engine_config: 搜索引擎具体配置参数
            
        Returns:
            创建的搜索引擎实例
        """
        # 创建引擎特定的配置
        config = ConfigFactory.create_config(engine_type, **engine_config)
        
        if engine_type == SearchEngineType.ARXIV.value:
            return ArxivSearchEngine(
                config=config,
                api_key=engine_config.get("api_key"),
                max_results=engine_config.get("max_results")
            )
        elif engine_type == SearchEngineType.GOOGLE_SCHOLAR.value:
            return GoogleScholarSearchEngine(
                config=config,
                api_key=engine_config.get("api_key"),
                max_results=engine_config.get("max_results")
            )
        else:
            raise ValueError(f"不支持的搜索引擎类型: {engine_type}")


class CompositeSearchEngine(SearchEngine):
    """组合多个搜索引擎的复合引擎"""
    
    def __init__(self, engines: List[SearchEngine] = None):
        self.engines = engines or []
    
    def add_engine(self, engine: SearchEngine):
        """添加搜索引擎"""
        self.engines.append(engine)
    
    def search(self, query: str, **kwargs) -> List[SearchResult]:
        """从所有添加的引擎中获取并合并搜索结果"""
        all_results = []
        for engine in self.engines:
            results = engine.search(query, **kwargs)
            all_results.extend(results)
        return all_results
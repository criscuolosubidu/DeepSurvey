from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
import requests
from dataclasses import dataclass

import arxiv
from src.utils.logger import SearchLogger, LogConfig


@dataclass
class SearchEngineConfig:
    """搜索引擎配置类"""
    default_max_results: int = 10
    default_market: str = "en-US"
    default_sort_by: str = arxiv.SortCriterion.Relevance
    arxiv_base_url: str = "http://export.arxiv.org/api/query"


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
            config: SearchEngineConfig = None, 
            api_key: Optional[str] = None, 
            max_results: Optional[int] = None
        ):
        self.config = config or SearchEngineConfig()
        self.api_key = api_key
        self.max_results = max_results or self.config.default_max_results
        self.base_url = self.config.arxiv_base_url
        self.logger = SearchLogger("arxiv_engine")
    
    def search(self, query: str, **kwargs) -> List[SearchResult]:
        self.logger.info("开始Arxiv搜索", query=query, **kwargs)
        return self.search_papers(query, **kwargs)
    
    def search_papers(self, query: str, **kwargs) -> List[SearchResult]:
        # 创建arxiv client
        client = arxiv.Client()

        max_results = kwargs.get('max_results', self.max_results)
        sort_by = kwargs.get('sort_by', self.config.default_sort_by)

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
    
    def __init__(self, config: SearchEngineConfig = None, api_key: str = None, max_results: Optional[int] = None):
        self.config = config or SearchEngineConfig()
        self.api_key = api_key
        self.max_results = max_results or self.config.default_max_results
    
    def search(self, query: str, **kwargs) -> List[SearchResult]:
        """实现基类的搜索方法，调用学术搜索策略"""
        return self.search_papers(query, **kwargs)
    
    def search_papers(self, query: str, **kwargs) -> List[SearchResult]:
        """实现Google Scholar搜索"""
        # 实际实现中需要使用第三方库或自建爬虫，因为Google Scholar没有官方API
        # 这里仅作为示例
        return [
            SearchResult(
                title="Google Scholar Paper Example",
                url="https://scholar.google.com/example",
                snippet="Example snippet from Google Scholar",
                source="Google Scholar"
            )
        ]


# 搜索引擎工厂
class SearchEngineFactory:
    """搜索引擎工厂，负责创建和管理搜索引擎实例"""
    
    @staticmethod
    def create_engine(engine_type: str, config: SearchEngineConfig = None, **engine_config) -> SearchEngine:
        """
        创建搜索引擎实例
        
        Args:
            engine_type: 搜索引擎类型('arxiv', 'google_scholar'等)
            config: 搜索引擎配置对象
            **engine_config: 搜索引擎具体配置参数
            
        Returns:
            创建的搜索引擎实例
        """
        config = config or SearchEngineConfig()
        
        if engine_type == "arxiv":
            return ArxivSearchEngine(
                config=config,
                api_key=engine_config.get("api_key"),
                max_results=engine_config.get("max_results")
            )
        elif engine_type == "google_scholar":
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
        
        # 可以在这里添加结果去重、排序等逻辑
        
        return all_results
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
    bing_base_url: str = "https://api.bing.microsoft.com/v7.0/search"


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


# 通用搜索引擎实现
class BingSearchEngine(SearchEngine, GeneralSearchStrategy):
    """Bing搜索引擎实现"""
    
    def __init__(self, config: SearchEngineConfig = None, api_key: str = None, max_results: Optional[int] = None):
        self.config = config or SearchEngineConfig()
        self.api_key = api_key
        self.max_results = max_results or self.config.default_max_results
        self.base_url = self.config.bing_base_url
        self.logger = SearchLogger("bing_engine")
    
    def search(self, query: str, **kwargs) -> List[SearchResult]:
        """实现基类的搜索方法，调用通用搜索策略"""
        self.logger.info("开始Bing搜索", query=query, **kwargs)
        return self.search_web(query, **kwargs)
    
    def search_web(self, query: str, **kwargs) -> List[SearchResult]:
        """实现通用网页搜索"""
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {
            "q": query,
            "count": kwargs.get("max_results", self.max_results),
            "mkt": kwargs.get("market", self.config.default_market)
        }
        
        self.logger.debug("执行Bing搜索", query=query, params=params)
        
        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            data = response.json()
            
            results = []
            # 解析Bing API返回的结果
            if "webPages" in data and "value" in data["webPages"]:
                for item in data["webPages"]["value"]:
                    results.append(SearchResult(
                        title=item.get("name", ""),
                        url=item.get("url", ""),
                        snippet=item.get("snippet", ""),
                        source="Bing"
                    ))
            self.logger.info("Bing搜索完成", found_results=len(results))
            return results
        except Exception as e:
            self.logger.error("Bing搜索出错", error=str(e), query=query)
            return []


# 搜索引擎工厂
class SearchEngineFactory:
    """搜索引擎工厂，负责创建和管理搜索引擎实例"""
    
    @staticmethod
    def create_engine(engine_type: str, config: SearchEngineConfig = None, **engine_config) -> SearchEngine:
        """
        创建搜索引擎实例
        
        Args:
            engine_type: 搜索引擎类型('arxiv', 'google_scholar', 'bing'等)
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
        elif engine_type == "bing":
            return BingSearchEngine(
                config=config,
                api_key=engine_config.get("api_key"),
                max_results=engine_config.get("max_results")
            )
        else:
            raise ValueError(f"不支持的搜索引擎类型: {engine_type}")


# 复合搜索引擎，可以组合多个搜索引擎
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


# 使用示例
def search_example():
    # 创建配置实例
    config = SearchEngineConfig()
    
    # 创建搜索日志记录器
    logger = SearchLogger("search_example")
    
    # 创建各种搜索引擎
    logger.info("初始化arXiv搜索引擎")
    arxiv_engine = SearchEngineFactory.create_engine(
        "arxiv", 
        config=config,
        max_results=5
    )
    
    # 假设我们有API密钥
    logger.info("初始化Bing搜索引擎")
    bing_engine = SearchEngineFactory.create_engine(
        "bing", 
        config=config,
        api_key="your_bing_api_key",
        max_results=5
    )
    
    # 创建复合搜索引擎
    logger.info("创建复合搜索引擎")
    composite_engine = CompositeSearchEngine()
    composite_engine.add_engine(arxiv_engine)
    composite_engine.add_engine(bing_engine)
    
    # 执行搜索
    query = "机器学习深度学习综述"
    logger.info("开始执行复合搜索", query=query)
    results = composite_engine.search(
        query, 
        max_results=10
    )
    
    # 处理结果
    logger.info(f"搜索完成，共获取{len(results)}条结果")
    for result in results:
        print(f"标题: {result.title}")
        print(f"来源: {result.source}")
        print(f"URL: {result.url}")
        print(f"摘要: {result.snippet}")
        print("-" * 50)


if __name__ == "__main__":
    # 运行示例
    search_example()

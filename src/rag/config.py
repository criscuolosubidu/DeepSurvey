from dataclasses import dataclass, field
from typing import Dict, Any, Optional, ClassVar
from enum import Enum


class SearchEngineType(Enum):
    """搜索引擎类型枚举"""
    ARXIV = "arxiv"
    GOOGLE_SCHOLAR = "google_scholar"
    GOOGLE = "google"


@dataclass
class BaseEngineConfig:
    """基础搜索引擎配置类"""
    max_results: int = 10
    timeout: int = 30  
    api_key: Optional[str] = None


@dataclass
class ArxivConfig(BaseEngineConfig):
    """Arxiv搜索引擎特定配置"""
    base_url: str = "http://export.arxiv.org/api/query"
    sort_by: Optional[str] = None


@dataclass
class GoogleScholarConfig(BaseEngineConfig):
    """Google Scholar搜索引擎特定配置"""
    base_url: str = "https://google.serper.dev/scholar" # 使用serper.dev的API
    hl: str = "en"
    as_sdt: str = "0,5"
    as_vis: str = "1"
    
  
@dataclass
class GoogleConfig(BaseEngineConfig):
    """Google搜索引擎特定配置"""
    gl: str = "cn"  # 地理位置
    hl: str = "zh-CN"  # 语言设置


class ConfigFactory:
    """配置工厂类，负责创建各种搜索引擎配置"""
    
    _config_map: ClassVar[Dict[str, type]] = {
        SearchEngineType.ARXIV.value: ArxivConfig,
        SearchEngineType.GOOGLE_SCHOLAR.value: GoogleScholarConfig,
        SearchEngineType.GOOGLE.value: GoogleConfig,
    }
    
    @classmethod
    def create_config(cls, engine_type: str, **kwargs) -> BaseEngineConfig:
        """
        创建并返回特定类型搜索引擎的配置对象
        
        Args:
            engine_type: 搜索引擎类型，必须是SearchEngineType中的一个值
            **kwargs: 配置参数，将覆盖默认值
            
        Returns:
            配置对象
            
        Raises:
            ValueError: 如果提供了不支持的搜索引擎类型
        """
        if engine_type not in cls._config_map:
            supported_types = ", ".join(cls._config_map.keys())
            raise ValueError(f"不支持的搜索引擎类型: {engine_type}. 支持的类型: {supported_types}")
        
        config_class = cls._config_map[engine_type]
        return config_class(**kwargs)
    
    @classmethod
    def register_config(cls, engine_type: str, config_class: type):
        """
        注册新的搜索引擎配置类
        
        Args:
            engine_type: 搜索引擎类型
            config_class: 配置类，必须是BaseEngineConfig的子类
        """
        if not issubclass(config_class, BaseEngineConfig):
            raise TypeError("配置类必须是BaseEngineConfig的子类")
        
        cls._config_map[engine_type] = config_class 
import logging
import os
import sys
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class LogConfig:
    """日志配置类"""
    log_level: int = logging.INFO
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    log_dir: str = "logs"
    log_file: Optional[str] = None
    console_output: bool = True
    file_output: bool = True


class LogManager:
    """日志管理器，负责创建和配置日志记录器"""
    
    _loggers: Dict[str, logging.Logger] = {}
    
    @classmethod
    def get_logger(cls, name: str, config: Optional[LogConfig] = None) -> logging.Logger:
        """
        获取或创建指定名称的日志记录器
        
        Args:
            name: 日志记录器名称
            config: 日志配置，如不提供则使用默认配置
            
        Returns:
            配置好的日志记录器
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        config = config or LogConfig()
        logger = logging.getLogger(name)
        
        # 避免重复配置
        if logger.handlers:
            return logger
            
        logger.setLevel(config.log_level)
        
        # 配置日志格式
        formatter = logging.Formatter(config.log_format, datefmt=config.date_format)
        
        # 添加控制台处理器
        if config.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # 添加文件处理器
        if config.file_output:
            if not os.path.exists(config.log_dir):
                os.makedirs(config.log_dir)
                
            log_file = config.log_file
            if not log_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_file = f"{name}_{timestamp}.log"
                
            file_path = os.path.join(config.log_dir, log_file)
            file_handler = logging.FileHandler(file_path, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        cls._loggers[name] = logger
        return logger


class SearchLogger:
    """搜索引擎专用日志类"""
    
    def __init__(self, name: str = "search_engine", config: Optional[LogConfig] = None):
        self.logger = LogManager.get_logger(name, config)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """记录信息级别日志"""
        self._log_with_context(self.logger.info, message, kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """记录警告级别日志"""
        self._log_with_context(self.logger.warning, message, kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """记录错误级别日志"""
        self._log_with_context(self.logger.error, message, kwargs)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """记录调试级别日志"""
        self._log_with_context(self.logger.debug, message, kwargs)
        
    def _log_with_context(self, log_func, message: str, context: Dict[str, Any]) -> None:
        """带上下文信息的日志记录"""
        if context:
            context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
            message = f"{message} | {context_str}"
        log_func(message)
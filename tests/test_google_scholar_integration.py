import unittest
import pytest
import json
import requests
import responses
import os
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

from src.rag.search_engine import GoogleScholarSearchEngine, SearchResult
from src.rag.config import GoogleScholarConfig, SearchEngineType

import pathlib

BASE_DIR = pathlib.Path(__file__).parent.parent
load_dotenv(BASE_DIR / '.env')

@pytest.mark.integration
class TestGoogleScholarIntegration(unittest.TestCase):
    """GoogleScholarSearchEngine集成测试"""
    
    def setUp(self):
        # 从环境变量获取API密钥，在实际测试时需要设置
        self.api_key = os.environ.get('GOOGLE_SCHOLAR_API_KEY')
        if not self.api_key:
            self.skipTest("缺少GOOGLE_SCHOLAR_API_KEY环境变量")
        
        self.config = GoogleScholarConfig(
            max_results=5,
            api_key=self.api_key,
            timeout=10
        )
        self.engine = GoogleScholarSearchEngine(config=self.config)
    
    @pytest.mark.integration
    def test_real_search(self):
        """测试实际的Google Scholar搜索功能"""
        query = "machine learning survey"
        results = self.engine.search(query, max_results=3)
        
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 3)
        
        for result in results:
            self.assertTrue(hasattr(result, 'title'))
            self.assertTrue(hasattr(result, 'url'))
            self.assertTrue(hasattr(result, 'snippet'))
            self.assertEqual(result.source, "Google Scholar")
            
            # 检查metadata字段
            self.assertIsNotNone(result.metadata)
            self.assertIn('year', result.metadata) # 年份可能为None
            self.assertIn('citedBy', result.metadata)
    
    @pytest.mark.integration
    def test_pagination(self):
        """测试分页功能"""
        query = "deep learning"
        
        # 请求超过一页的结果
        results = self.engine.search(query, max_results=15)
        
        # 验证结果数量
        self.assertGreater(len(results), 10)  # 应该大于一页(10条)
        self.assertLessEqual(len(results), 15)  # 不超过请求的数量
        
        # 验证所有结果的基本字段
        for result in results:
            self.assertTrue(hasattr(result, 'title'))
            self.assertEqual(result.source, "Google Scholar")
    
    @pytest.mark.integration
    def test_search_with_parameters(self):
        """测试带有额外参数的搜索"""
        query = "artificial intelligence ethics"
        
        # 使用额外参数指定搜索时间范围(2020年至今)
        results = self.engine.search(query, max_results=3, as_ylo=2020)
        
        self.assertGreater(len(results), 0)
        
        for result in results:
            # 如果结果中有年份信息，确保它大于等于2020
            if result.metadata.get('year') is not None:
                # 年份可能是整数或字符串，需要正确处理
                year_value = result.metadata['year']
                if isinstance(year_value, str) and year_value.isdigit():
                    self.assertGreaterEqual(int(year_value), 2020)
                elif isinstance(year_value, int):
                    self.assertGreaterEqual(year_value, 2020)


class TestGoogleScholarMock(unittest.TestCase):
    """使用mock测试Google Scholar搜索引擎"""
    
    def setUp(self):
        self.config = GoogleScholarConfig(
            max_results=5,
            api_key="mock_api_key",
            timeout=10
        )
        self.engine = GoogleScholarSearchEngine(config=self.config)
        
        # 模拟响应数据
        self.mock_response_data = {
            "organic": [
                {
                    "title": "机器学习: 一个综述",
                    "link": "https://example.com/paper1",
                    "snippet": "这是一篇关于机器学习的综述论文...",
                    "year": "2022",
                    "citedBy": 120,
                    "id": "abc123",
                    "pdfUrl": "https://example.com/paper1.pdf",
                    "publicationInfo": "Journal of Machine Learning"
                },
                {
                    "title": "深度学习的最新进展",
                    "link": "https://example.com/paper2",
                    "snippet": "这篇论文回顾了深度学习的最新进展...",
                    "year": "2021",
                    "citedBy": 85,
                    "id": "def456",
                    "publicationInfo": "Neural Networks"
                }
            ]
        }
    
    @responses.activate
    def test_search_with_mock(self):
        """使用mock响应测试搜索功能"""
        # 配置mock响应
        responses.add(
            responses.POST,
            self.config.base_url,
            json=self.mock_response_data,
            status=200
        )
        
        # 执行搜索
        results = self.engine.search("machine learning", max_results=2)
        
        # 验证结果
        self.assertEqual(len(results), 2)
        
        # 验证第一个结果
        self.assertEqual(results[0].title, "机器学习: 一个综述")
        self.assertEqual(results[0].url, "https://example.com/paper1")
        self.assertEqual(results[0].snippet, "这是一篇关于机器学习的综述论文...")
        self.assertEqual(results[0].source, "Google Scholar")
        self.assertEqual(results[0].metadata["year"], "2022")
        self.assertEqual(results[0].metadata["citedBy"], 120)
        self.assertEqual(results[0].metadata["id"], "abc123")
        self.assertEqual(results[0].metadata["pdfUrl"], "https://example.com/paper1.pdf")
        self.assertEqual(results[0].metadata["publicationInfo"], "Journal of Machine Learning")
        
        # 验证第二个结果
        self.assertEqual(results[1].title, "深度学习的最新进展")
        self.assertEqual(results[1].source, "Google Scholar")
    
    @responses.activate
    def test_pagination_with_mock(self):
        """使用mock响应测试分页功能"""
        # 第一页响应
        responses.add(
            responses.POST,
            self.config.base_url,
            json=self.mock_response_data,
            status=200
        )
        
        # 第二页响应 - 不同的数据
        page2_data = {
            "organic": [
                {
                    "title": "强化学习综述",
                    "link": "https://example.com/paper3",
                    "snippet": "强化学习的综合回顾...",
                    "year": "2023",
                    "citedBy": 50
                }
            ]
        }
        responses.add(
            responses.POST,
            self.config.base_url,
            json=page2_data,
            status=200
        )
        
        # 执行搜索
        results = self.engine.search("machine learning", max_results=3)
        
        # 验证结果
        self.assertEqual(len(results), 3)
        self.assertEqual(results[2].title, "强化学习综述")
        self.assertEqual(results[2].metadata["year"], "2023")
    
    @responses.activate
    def test_error_handling(self):
        """测试错误处理"""
        # 模拟HTTP错误
        responses.add(
            responses.POST,
            self.config.base_url,
            status=403
        )
        
        # 执行搜索
        results = self.engine.search("machine learning", max_results=2)
        
        # 验证结果为空列表，但不会抛出异常
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()

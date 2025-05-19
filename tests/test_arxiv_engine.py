import unittest
from unittest.mock import patch, MagicMock
import arxiv

from src.rag.search_engine import ArxivSearchEngine, SearchResult
from src.rag.config import ArxivConfig


class TestArxivSearchEngine(unittest.TestCase):
    
    def setUp(self):
        """测试前的设置"""
        self.config = ArxivConfig(max_results=5)
        self.engine = ArxivSearchEngine(config=self.config)
    
    def test_init(self):
        """测试初始化参数是否正确"""
        self.assertEqual(self.engine.config.max_results, 5)
        self.assertEqual(self.engine.config.base_url, "http://export.arxiv.org/api/query")
    
    @patch('arxiv.Client')
    def test_search_papers(self, mock_client):
        """测试search_papers方法"""
        # 模拟arxiv API响应
        mock_result = MagicMock()
        mock_result.title = "测试论文标题"
        mock_result.entry_id = "http://arxiv.org/abs/1234.5678"
        mock_result.summary = "这是一篇测试论文的摘要"
        
        # 创建作者MagicMock对象，确保每个作者有name属性
        author1 = MagicMock()
        author1.name = "张三"
        author2 = MagicMock()
        author2.name = "李四"
        mock_result.authors = [author1, author2]
        
        mock_result.published = "2023-01-01"
        mock_result.categories = ["cs.AI", "cs.LG"]
        
        # 设置模拟客户端返回值
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.results.return_value = [mock_result]
        
        # 执行搜索
        results = self.engine.search_papers("machine learning")
        
        # 验证结果
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "测试论文标题")
        self.assertEqual(results[0].url, "http://arxiv.org/abs/1234.5678")
        self.assertEqual(results[0].snippet, "这是一篇测试论文的摘要")
        self.assertEqual(results[0].source, "arXiv")
        self.assertEqual(results[0].metadata["authors"], ["张三", "李四"])
        self.assertEqual(results[0].metadata["categories"], ["cs.AI", "cs.LG"])
    
    def test_invalid_max_results(self):
        """测试无效的max_results参数"""
        with self.assertRaises(TypeError):
            self.engine.search_papers("machine learning", max_results="invalid")
    
    @patch('arxiv.Client')
    def test_search_with_sort_by(self, mock_client):
        """测试带有sort_by参数的搜索"""
        # 模拟结果
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.results.return_value = []
        
        # 测试字符串形式的sort_by参数
        self.engine.search_papers("machine learning", sort_by="relevance")
        
        # 验证搜索参数
        search_arg = mock_client_instance.results.call_args[0][0]
        self.assertEqual(search_arg.sort_by, arxiv.SortCriterion.Relevance)


if __name__ == "__main__":
    unittest.main() 
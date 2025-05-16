import unittest
import pytest
import arxiv
from src.rag.search_engine import ArxivSearchEngine, SearchEngineConfig


@pytest.mark.integration
class TestArxivIntegration(unittest.TestCase):
    """ArxivSearchEngine集成测试"""
    
    def setUp(self):
        self.config = SearchEngineConfig(default_max_results=3)
        self.engine = ArxivSearchEngine(config=self.config)
    
    @pytest.mark.integration
    def test_real_search(self):
        """测试实际的arXiv搜索功能"""
        query = "machine learning survey"
        results = self.engine.search(query, max_results=2)
        
        self.assertGreater(len(results), 0)
        
        for result in results:
            self.assertTrue(hasattr(result, 'title'))
            self.assertTrue(hasattr(result, 'url'))
            self.assertTrue(hasattr(result, 'snippet'))
            self.assertEqual(result.source, "arXiv")
            
            self.assertIn('authors', result.metadata)
            self.assertIn('published', result.metadata)
            self.assertIn('categories', result.metadata)
    
    @pytest.mark.integration
    def test_search_with_different_sort(self):
        """测试不同排序标准的搜索"""
        query = "deep learning"
        
        results_relevance = self.engine.search(query, max_results=2, sort_by=arxiv.SortCriterion.Relevance)
        results_lastUpdated = self.engine.search(query, max_results=2, sort_by=arxiv.SortCriterion.LastUpdatedDate)
        
        self.assertGreater(len(results_relevance), 0)
        self.assertGreater(len(results_lastUpdated), 0)

        for result in results_relevance + results_lastUpdated:
            self.assertTrue(hasattr(result, 'title'))
            self.assertEqual(result.source, "arXiv")


if __name__ == "__main__":
    unittest.main() 
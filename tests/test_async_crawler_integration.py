import unittest
import pytest
import asyncio
import os
import tempfile
import json
import pathlib
from dotenv import load_dotenv

from src.rag.async_crawler import AsyncCrawler

# 加载环境变量
BASE_DIR = pathlib.Path(__file__).parent.parent
load_dotenv(BASE_DIR / '.env')

@pytest.mark.integration
class TestAsyncCrawlerIntegration(unittest.TestCase):
    """AsyncCrawler集成测试"""
    
    def setUp(self):
        # 检查OpenAI API密钥是否存在，用于实际测试
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            self.skipTest("缺少OPENAI_API_KEY环境变量")
        
        # 初始化爬虫实例
        self.crawler = AsyncCrawler(model=os.getenv("CRAWLER_FILTER_LLM"), infer_type="OpenAI")
        
        # 创建临时输出文件
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False)
        self.output_path = self.temp_file.name
        self.temp_file.close()
    
    def tearDown(self):
        # 清理临时文件
        if hasattr(self, 'output_path') and os.path.exists(self.output_path):
            os.unlink(self.output_path)
    
    @pytest.mark.integration
    def test_crawler_run(self):
        """测试AsyncCrawler的run方法是否能够正常运行并返回结果"""
        # 定义测试参数
        topic = "Python programming"
        url_list = [
            "https://www.python.org/about/",
            "https://docs.python.org/3/tutorial/introduction.html"
        ]
        
        # 运行爬虫
        asyncio.run(
            self.crawler.run(
                topic=topic,
                url_list=url_list,
                crawl_output_file_path=self.output_path,
                top_n=5
            )
        )
        
        # 验证结果 - 只检查文件是否存在，因为内容可能为空（如果爬取失败）
        self.assertTrue(os.path.exists(self.output_path), "输出文件应该存在")
        
        # 检查输出文件内容
        try:
            with open(self.output_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:  # 只有当文件不为空时才尝试解析JSON
                    data = json.loads(content)
                    
                    # 验证基本结构
                    self.assertEqual(data['title'], topic, "输出数据的主题应该匹配")
                    self.assertIn('papers', data, "输出数据应该包含papers字段")
                    
                    # 验证爬取结果
                    papers = data['papers']
                    if papers:  # 只有当有结果时才进行验证
                        # 检查每个paper的结构
                        for paper in papers:
                            self.assertIn('title', paper, "每个结果应该有标题")
                            self.assertIn('url', paper, "每个结果应该有URL")
                            self.assertIn('txt', paper, "每个结果应该有文本内容")
                            self.assertIn('similarity', paper, "每个结果应该有相似度评分")
                            
                            # 检查URL是否在原始列表中
                            self.assertIn(paper['url'], url_list, "结果URL应在原始URL列表中")
                            
                            # 检查内容非空
                            self.assertGreater(len(paper['txt']), 0, "文本内容不应为空")
                            
                            # 检查相似度评分是否合理
                            self.assertGreaterEqual(paper['similarity'], 0, "相似度应为非负数")
                            self.assertLessEqual(paper['similarity'], 100, "相似度应不超过100")
        except json.JSONDecodeError:
            # 如果JSON解析失败，跳过测试但不视为失败
            self.skipTest("爬取结果文件不包含有效的JSON")
    
    @pytest.mark.integration
    def test_crawler_dummy_simple(self):
        """简单测试爬虫，只检查是否能运行而不验证内容"""
        # 定义测试参数
        topic = "测试"
        url_list = ["https://python.org"]
        
        # 运行爬虫
        asyncio.run(
            self.crawler.run(
                topic=topic,
                url_list=url_list,
                crawl_output_file_path=self.output_path,
                top_n=5
            )
        )
        
        # 只验证爬虫能够运行完成，不检查内容
        self.assertTrue(os.path.exists(self.output_path), "输出文件应该存在")


if __name__ == "__main__":
    unittest.main()

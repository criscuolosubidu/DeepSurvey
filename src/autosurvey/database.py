from tqdm import tqdm
from src.autosurvey.utils import tokenCounter
from src.rag.search_engine import SearchEngineFactory, SearchEngineConfig


class database():

    def __init__(self, db_path, embedding_model=None) -> None:
        self.search_engine_config = SearchEngineConfig(default_max_results=10)
        self.search_engine = SearchEngineFactory.create_engine(
            "arxiv", 
            config=self.search_engine_config
        )
        
        # 如果提供了embedding_model，保留原来的嵌入模型以兼容混合检索方式
        if embedding_model:
            print("Use Model at: " + embedding_model)
            self.embedding_model = SentenceTransformer(embedding_model, trust_remote_code=True)
            self.embedding_model.to(torch.device('cuda'))
        else:
            self.embedding_model = None
            
        # 初始化TinyDB
        self.db = TinyDB(f'{db_path}/arxiv_paper_db.json')
        self.table = self.db.table('cs_paper_info')
        self.User = Query()
        self.token_counter = tokenCounter()
        
    def get_ids_from_query(self, query, num, shuffle=False):
        """
        根据查询文本获取相关文档ID（使用搜索引擎）
        
        参数:
            query: 查询文本
            num: 返回的结果数量
            shuffle: 是否打乱结果（未实现）
            
        返回:
            list: 与查询文本最相关的num个文档ID
        """
        # 使用搜索引擎进行查询
        search_results = self.search_engine.search(query, max_results=num)
        
        # 从URL中提取arXiv ID
        # arXiv URL通常格式为http://arxiv.org/abs/XXXX.XXXXX
        ids = []
        for result in search_results:
            url = result.url
            # 从URL中提取论文ID
            arxiv_id = url.split('/')[-1]
            ids.append(arxiv_id)
            
        return ids
    
    def get_titles_from_citations(self, citations):
        """
        根据引用文本获取相关文档ID
        
        参数:
            citations: 引用文本列表
            
        返回:
            list: 每个引用文本最相关的文档ID
        """
        # 对每个引用使用搜索引擎查询
        ids = []
        for citation in tqdm(citations):
            results = self.search_engine.search(citation, max_results=1)
            if results:
                # 从URL中提取arXiv ID
                arxiv_id = results[0].url.split('/')[-1]
                ids.append(arxiv_id)
            else:
                # 如果没有找到结果，添加一个空值
                ids.append(None)
                
        return [id for id in ids if id is not None]

    def get_ids_from_queries(self, queries, num, shuffle=False):
        """
        根据多个查询文本批量获取相关文档ID
        
        参数:
            queries: 查询文本列表
            num: 每个查询返回的结果数量
            shuffle: 是否打乱结果（未实现）
            
        返回:
            list: 列表的列表，每个内部列表包含与对应查询最相关的num个文档ID
        """
        all_ids = []
        for query in tqdm(queries):
            ids = self.get_ids_from_query(query, num)
            all_ids.append(ids)
            
        return all_ids
    
    def get_date_from_ids(self, ids):
        """
        根据文档ID获取发布日期
        
        参数:
            ids: 文档ID列表
            
        返回:
            list: 对应文档的发布日期列表
        """
        result = self.table.search(self.User.id.one_of(ids))
        dates = [r['date'] for r in result]
        return dates

    def get_title_from_ids(self, ids):
        """
        根据文档ID获取标题
        
        参数:
            ids: 文档ID列表
            
        返回:
            list: 对应文档的标题列表
        """
        result = self.table.search(self.User.id.one_of(ids))
        titles = [r['title'] for r in result]
        return titles

    def get_abs_from_ids(self, ids):
        """
        根据文档ID获取摘要
        
        参数:
            ids: 文档ID列表
            
        返回:
            list: 对应文档的摘要列表
        """
        result = self.table.search(self.User.id.one_of(ids))
        abs_l = [r['abs'] for r in result]
        return abs_l

    def get_paper_info_from_ids(self, ids):
        """
        根据文档ID获取完整论文信息
        
        参数:
            ids: 文档ID列表
            
        返回:
            list[dict]: 包含对应文档完整信息的字典列表
                这里面字典包含的信息如下：
                id: 文档ID str
                title: 文档标题 str
                abs: 文档摘要 str
                date: 文档发布日期 str
                cat: 文档分类 str
                authors: 文档作者 list
        """
        result = self.table.search(self.User.id.one_of(ids))
        return result
    
    def get_paper_from_ids(self, ids, max_len=1500):
        """
        根据文档ID获取论文内容
        
        参数:
            ids: 文档ID列表
            max_len: 截断长度，默认1500个token
            
        返回:
            list: 经过长度截断的论文内容列表
        """
        loaded_data = {}
        with h5py.File('./paper_content.h5', 'r') as f:
            for key in f.keys():
                if key in ids:
                    loaded_data[key] = str(f[key][()])
                if len(ids) == len(loaded_data):
                    break
        print(loaded_data[list(loaded_data.keys())[0]])
        return [self.token_counter.text_truncation(loaded_data[_], max_len) for _ in ids]
    
    # 以下是添加的新方法，支持混合检索方式
    
    def use_hybrid_search(self, query, num, title_weight=0.3):
        """
        使用混合搜索方法（向量搜索+搜索引擎）获取相关文档ID
        
        参数:
            query: 查询文本
            num: 返回的结果数量
            title_weight: 标题匹配的权重
            
        返回:
            list: 混合搜索结果的文档ID列表
        """
        # 确保嵌入模型已初始化
        if not self.embedding_model:
            return self.get_ids_from_query(query, num)
            
        # 使用搜索引擎获取结果
        search_engine_ids = self.get_ids_from_query(query, num)
        
        # 尝试使用本地向量搜索获取结果（如果有向量索引）
        try:
            # 这里保留向量搜索的能力，但不再加载索引，而是尝试用API获取
            # 要使用这个功能，需要保留原始的faiss索引文件并在初始化时加载
            vector_ids = self._get_ids_from_query_using_vector(query, num)
            
            # 合并结果并去重
            result_ids = list(set(search_engine_ids + vector_ids))
            if len(result_ids) > num:
                result_ids = result_ids[:num]
                
            return result_ids
        except Exception as e:
            # 如果向量搜索失败，只返回搜索引擎结果
            print(f"向量搜索失败，仅使用搜索引擎结果: {e}")
            return search_engine_ids
    
    def _get_ids_from_query_using_vector(self, query, num):
        """
        使用向量搜索获取文档ID（内部方法，需要嵌入模型和索引）
        
        参数:
            query: 查询文本
            num: 结果数量
            
        返回:
            list: 向量搜索结果的文档ID列表
        """
        # 此方法需要外部访问API或保留原始向量索引的逻辑
        # 这里简单返回空列表，实际使用时可以实现接口调用
        return []
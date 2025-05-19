# DeepSurvey

## 项目介绍

DeepSurvey 是一个创新的自动化综述生成工具，旨在帮助用户通过输入研究主题，自动进行深度信息搜索并生成结构化的综述报告。项目利用先进的人工智能技术，简化了学术和行业研究中的文献调研与报告撰写流程，为用户提供高效、便捷的体验。

## 核心功能与技术实现

### 1. 基于 MultiAgent 的复杂深度搜索

DeepSurvey 采用多智能体（MultiAgent）架构，通过协同工作实现高效的主题相关信息检索。每个智能体负责不同的搜索任务，结合实时网络搜索和数据库查询，确保信息的全面性和准确性。

### 2. 高级报告生成机制

项目基于 RAG（Retrieval-Augmented Generation）与卷积 MapReduce 方法（参考 [LLMxMapReduce](https://github.com/thunlp/LLMxMapReduce)），对检索到的信息进行深度分析与整合，生成逻辑清晰、内容详实的综述报告。具体实现包括：

- **信息筛选与聚类**：通过 MapReduce 机制对海量数据进行分片处理和结构化组织。
- **内容生成**：结合 RAG 技术，确保生成报告的语义准确性和上下文连贯性。

### 3. 前端实现

DeepSurvey 提供了一个现代化的前端界面，兼顾用户体验与功能性，主要特性包括：

- **身份验证登录**：支持安全的用户认证，确保数据隐私与访问控制。
- **优雅的用户界面**：采用响应式设计，提供直观的操作体验，适配多种设备。
- **生成内容展示**：以清晰的格式展示生成的综述报告，支持下载和在线预览。

## 快速开始


1. 克隆仓库：
  
  ```bash
  git clone https://github.com/your-username/DeepSurvey.git
  ```
  
2. 安装依赖：
  
  ```bash
  pip install -r requirements.txt
  ```

3. 配置环境变量（可选）：

   创建`.env`文件在项目根目录，配置以下变量：
   ```
   # 翻译
   TRANSLATOR_MODEL="您的模型ID"
   TRANSLATOR_API_URL="您的API URL"
   TRANSLATOR_API_KEY="您的API密钥"
   ```
  
4. 启动服务：
  
  ```bash
  python main.py
  ```

## 搜索引擎配置系统

DeepSurvey 提供了一个灵活的搜索引擎配置系统，用于管理各种搜索引擎的配置：

### 使用示例

```python
# 导入配置相关类
from src.utils.config import ConfigFactory, SearchEngineType
from src.rag.search_engine import SearchEngineFactory

# 使用默认配置创建 Arxiv 搜索引擎
arxiv_engine = SearchEngineFactory.create_engine(SearchEngineType.ARXIV.value)

# 使用自定义配置创建 Google Scholar 搜索引擎
gs_engine = SearchEngineFactory.create_engine(
    SearchEngineType.GOOGLE_SCHOLAR.value,
    max_results=20,
    include_patents=True,
    api_key="your_api_key"
)

# 搜索示例
results = arxiv_engine.search("机器学习最新进展")
```

### 扩展自定义搜索引擎

您可以通过以下步骤轻松扩展系统支持新的搜索引擎：

1. 在 `src/rag/config.py` 中添加新的配置类
2. 在 `ConfigFactory` 中注册新的配置类
3. 在 `src/rag/search_engine.py` 中实现相应的搜索引擎类
4. 在 `SearchEngineFactory` 中添加新搜索引擎的创建逻辑

```python
# 步骤1: 添加自定义配置类
@dataclass
class MyCustomConfig(BaseEngineConfig):
    custom_param: str = "default_value"

# 步骤2: 注册配置类
ConfigFactory.register_config("my_custom_engine", MyCustomConfig)

# 步骤3-4: 实现搜索引擎并更新工厂(在相应的文件中)
```

## 贡献

欢迎对 DeepSurvey 提出建议或贡献代码！请提交 Issue 或 Pull Request，我们期待您的参与。

## 许可证

本项目采用 AGPL 许可证，详情见 [LICENSE](LICENSE) 文件。

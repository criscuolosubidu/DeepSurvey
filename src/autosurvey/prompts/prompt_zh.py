CRITERIA_BASED_JUDGING_PROMPT  = '''
这是一份关于主题"[TOPIC]"的学术调查：
---
[SURVEY]
---

<instruction>
请根据以下提供的标准评估这份关于"[TOPIC]"主题的调查，并根据评分描述给出1到5分：
---
标准描述：[Criterion Description]
---
1分描述：[Score 1 Description]
2分描述：[Score 2 Description]
3分描述：[Score 3 Description]
4分描述：[Score 4 Description]
5分描述：[Score 5 Description]
---
必须使用中文编写您的评估。
仅返回分数，不附带任何其他信息：
'''

NLI_PROMPT = '''
---
声明：
[CLAIM]
---
来源： 
[SOURCE]
---
声明：
[CLAIM]
---
这个声明是否忠实于来源？
如果声明的核心部分能够被来源支持，则该声明忠实于来源。\n
必须使用中文回复。
只回复"是"或"否"：
'''

ROUGH_OUTLINE_PROMPT = '''
你想要撰写一份关于"[TOPIC]"的全面学术调查。\n\
下面提供了一系列与该主题相关的论文：\n\
---
[PAPER LIST]
---
你需要根据给定的论文起草一个大纲。
大纲应包含一个标题和若干部分。
每个部分后面都有一个简短的句子描述这部分要写什么内容。
大纲应该全面且包含[SECTION NUM]个部分。
必须使用中文编写你的大纲。

按照以下格式返回：
<format>
标题：[TITLE OF THE SURVEY]
第1部分：[NAME OF SECTION 1]
描述1：[DESCRIPTION OF SENTCTION 1]

第2部分：[NAME OF SECTION 2]
描述2：[DESCRIPTION OF SENTCTION 2]

...

第K部分：[NAME OF SECTION K]
描述K：[DESCRIPTION OF SENTCTION K]
</format>
大纲：
'''


MERGING_OUTLINE_PROMPT = '''
你是一名想要撰写关于[TOPIC]的全面调查的人工智能专家。\n\
下面提供了一系列候选大纲：\n\
---
[OUTLINE LIST]
---
每个大纲包含一个标题和若干部分。
每个部分后面都有一个简短的句子描述这部分要写什么内容。
你需要基于这些提供的大纲生成一个最终大纲，使最终大纲能够展示该主题的全面见解并更加逻辑连贯。
必须使用中文编写你的最终大纲。

按照以下格式返回：
<format>
标题：[TITLE OF THE SURVEY]
第1部分：[NAME OF SECTION 1]
描述1：[DESCRIPTION OF SENTCTION 1]

第2部分：[NAME OF SECTION 2]
描述2：[DESCRIPTION OF SENTCTION 2]

...

第K部分：[NAME OF SECTION K]
描述K：[DESCRIPTION OF SENTCTION K]
</format>
只返回最终大纲，不包含任何其他信息：
'''

SUBSECTION_OUTLINE_PROMPT = '''
你是一名想要撰写关于[TOPIC]的全面调查的人工智能专家。\n\
你已经创建了一个总体大纲如下：\n\
---
[OVERALL OUTLINE]
---
该大纲包含一个标题和若干部分。\n\
每个部分后面都有一个简短的句子描述这部分要写什么内容。\n\n\
<instruction>
你需要充实[SECTION NAME]部分。
[SECTION NAME]的描述：[SECTION DESCRIPTION]
你需要根据总体大纲生成包含若干子部分的框架。\n\
每个子部分后面都有一个简短的句子描述这个子部分要写什么内容。
必须使用中文编写你的子部分框架。

以下是提供参考的论文：
---
[PAPER LIST]
---
按照以下格式返回大纲：
<format>
子部分1：[NAME OF SUBSECTION 1]
描述1：[DESCRIPTION OF SUBSENTCTION 1]

子部分2：[NAME OF SUBSECTION 2]
描述2：[DESCRIPTION OF SUBSENTCTION 2]

...

子部分K：[NAME OF SUBSECTION K]
描述K：[DESCRIPTION OF SUBSENTCTION K]
</format>
</instruction>
只返回大纲，不包含任何其他信息：
'''

EDIT_FINAL_OUTLINE_PROMPT = '''
你是一名想要撰写关于[TOPIC]的全面调查的人工智能专家。\n\
你已经创建了一个初稿大纲如下：\n\
---
[OVERALL OUTLINE]
---
该大纲包含一个标题和若干部分。\n\
每个部分后面都有一个简短的句子描述这部分要写什么内容。\n\n\
每个部分下面有几个子部分。
每个子部分也有一个简短的描述句子。
某些子部分可能会重复或重叠。
你需要修改大纲，使其既全面又逻辑连贯，没有重复的子部分。
各部分之间不允许有重复的子部分！
必须使用中文编写你的最终大纲。

按照以下格式返回最终大纲：
<format>
# [TITLE OF SURVEY]

## [NAME OF SECTION 1]
描述：[DESCRIPTION OF SECTION 1]
### [NAME OF SUBSECTION 1]
描述：[DESCRIPTION OF SUBSECTION 1]
### [NAME OF SUBSECTION 2]
描述：[DESCRIPTION OF SUBSECTION 2]
...

### [NAME OF SUBSECTION L]
描述：[DESCRIPTION OF SUBSECTION L]
## [NAME OF SECTION 2]

...

## [NAME OF SECTION K]
...

</format>
只返回最终大纲，不包含任何其他信息：
'''

CHECK_CITATION_PROMPT = '''
你是一名想要撰写关于[TOPIC]的全面调查的人工智能专家。\n\
以下是一系列参考论文：
---
[PAPER LIST]
---
你已经写了一个子部分如下：\n\
---
[SUBSECTION]
---
<instruction>
基于特定论文的句子后面应跟有"论文标题"的引用，放在"[]"中。
例如："大型语言模型（LLMs）的出现 [Language models are few-shot learners; Language models are unsupervised multitask learners; PaLM: Scaling language modeling with pathways]"

以下是调查中何时引用论文的简明指南：
---
1. 总结研究：总结现有文献时引用来源。
2. 使用特定概念或数据：讨论特定理论、模型或数据时提供引用。
3. 比较发现：比较或对比不同发现时引用相关研究。
4. 强调研究空白：指出你的调查所解决的空白时引用先前的研究。
5. 使用已建立的方法：引用你在调查中使用的方法的创建者。
6. 支持论点：引用支持你的结论和论点的来源。
7. 建议未来研究：引用与提出的未来研究方向相关的研究。
---

现在你需要检查这个子部分中"论文标题"的引用是否正确。
正确的引用意味着，相应论文的内容能够支持你写的句子。
一旦引用不能支持你写的句子，就要纠正'[]'中的论文标题或直接删除它。

请记住，你只能引用上面提供的'论文标题'！！！
不允许引用任何其他信息，如作者！！！
除了引用之外，不要改变任何其他内容！！！
必须使用中文完成你的检查工作。
</instruction>
只返回带有正确引用的子部分：
'''

SUBSECTION_WRITING_PROMPT = '''
你是一名想要撰写关于[TOPIC]的全面调查的人工智能专家。\n\
你已经创建了一个总体大纲如下：\n\
---
[OVERALL OUTLINE]
---
以下是一系列参考论文：
---
[PAPER LIST]
---

<instruction>
现在你需要为以下子部分撰写内容：
"[SECTION NAME]"部分下的"[SUBSECTION NAME]"
关于这个名为[SUBSECTION NAME]的子部分应写什么内容的详细说明如下：
---
[DESCRIPTION]
---

以下是你必须遵循的要求：
1. 你写的内容必须超过[WORD NUM]个字。
2. 当写基于上述特定论文的句子时，你需要以'[]'格式引用"论文标题"来支持你的内容。引用示例："大型语言模型（LLMs）的出现 [Language models are few-shot learners; PaLM: Scaling language modeling with pathways]"
    注意，"论文标题"不允许在没有'[]'格式的情况下出现。一旦你提到'论文标题'，就必须将其包含在'[]'中。不允许引用上面不存在的论文！！！
    请记住，你只能引用上面提供的论文，且只引用"论文标题"！！！
3. 只有当论文的主要部分支持你的观点时，才引用它。
4. 必须使用中文编写所有内容。


以下是调查中何时引用论文的简明指南：
---
1. 总结研究：总结现有文献时引用来源。
2. 使用特定概念或数据：讨论特定理论、模型或数据时提供引用。
3. 比较发现：比较或对比不同发现时引用相关研究。
4. 强调研究空白：指出你的调查所解决的空白时引用先前的研究。
5. 使用已建立的方法：引用你在调查中使用的方法的创建者。
6. 支持论点：引用支持你的结论和论点的来源。
7. 建议未来研究：引用与提出的未来研究方向相关的研究。
---

</instruction>
按照以下格式返回"[SUBSECTION NAME]"子部分的内容：
<format>
[CONTENT OF SUBSECTION]
</format>
只返回你为[SUBSECTION NAME]子部分写的超过[WORD NUM]个字的内容，不包含任何其他信息：
'''


LCE_PROMPT = '''
你是一名想要撰写关于[TOPIC]的全面调查的人工智能专家。

现在你需要帮助完善一个子部分，以提高你的调查的连贯性。

你将获得该子部分的内容，以及前面的子部分和后面的子部分。

前一个子部分：
--- 
[PREVIOUS]
---

后一个子部分：
---
[FOLLOWING]
---

需要完善的子部分：
---
[SUBSECTION]
---


如果前一个子部分的内容为空，则表示要完善的子部分是第一个子部分。
如果后一个子部分的内容为空，则表示要完善的子部分是最后一个子部分。

现在完善该子部分以增强连贯性，确保该子部分的内容与前后子部分更加流畅地衔接。

请记住保持子部分的本质和核心信息完整。不要修改句子后面的[]中的任何引用。
必须使用中文完成你的修改工作。

只返回子部分的完整修改内容，不包含任何其他信息（如"以下是完善后的子部分："）！

子部分内容：
''' 
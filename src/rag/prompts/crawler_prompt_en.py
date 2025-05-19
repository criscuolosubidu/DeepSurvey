# crawl4ai prompts
PAGE_REFINE_PROMPT = """Analyze and process the following web page content related to '{topic}'. Output the main body text, removing image links, website URLs, advertisements, meaningless repeated characters, etc. Summarization of the content is prohibited, and all information related to the topic should be retained.

Original web page content:
{raw_content}

[Output requirements]
- Title: <TITLE>Your title</TITLE>
- Filtered text: <CONTENT>Filtered text</CONTENT> 
"""

SIMILARITY_PROMPT = """Evaluate the quality of the following content retrieved from the internet based on the given topic, and give a suitable title about the content. Provide a critical and strict assessment.

Topic: {topic}  
Content: {content}  

Evaluate the content based on the following dimensions:  

1. **Relevance to the topic**: Assess whether the content can be considered a subset or expansion of the topic.  
2. **Usability for writing about the topic**: Consider factors such as text length (e.g., very short texts have lower reference value), presence of garbled characters, and overall text quality.  

Provide a rationale for your evaluation before assigning scores. Score each dimension on a scale of 0-100, where 0 indicates no relevance and 100 indicates perfect relevance. Calculate the final average score after scoring each dimension.  

Enclose the scores in `<SCORE></SCORE>` tags. For example: `<SCORE>78</SCORE>` 
Enclose the title in `<TITLE></TITLE>` tags. For example: `<TITLE>Title</TITLE>` 

Example response:  
Rationale: ...  
Relevance score: <SCORE>89</SCORE>
Title: <TITLE>Title</TITLE>
"""
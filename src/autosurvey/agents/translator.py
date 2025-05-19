import re 
import concurrent.futures 
import time
from src.autosurvey.model import APIModel
from src.autosurvey.prompts.prompt_en2zh import EN_TO_ZH_PROMPT
from src.autosurvey.config import TRANSLATOR_CONFIG


class Translator:

    def __init__(self, model: str, api_key: str, api_url: str):
        self.model = model
        self.api_key = api_key
        self.api_url = api_url
        self.api_model = APIModel(self.model, self.api_key, self.api_url)

    def _extract_translation(self, response: str) -> str:
        response = response.strip()
        if response == "<REFERENCES>":
            return "<REFERENCES>"

        match = re.search(r"<BEGIN_TRANSLATION>\s*(.*?)\s*<END_TRANSLATION>", response, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        else:
            print("Warning: Translation markers not found in response, and it's not a reference marker.")
            return response

    def translate_text(self, text: str) -> str:
        """翻译纯文本，如果检测到参考文献标记则不翻译"""
        if not text:
            return ""
        prompt = EN_TO_ZH_PROMPT.format(text=text)
        response = self.api_model.chat(prompt)
        translated_text = self._extract_translation(response)
        return translated_text

    def translate_md_file(self, input_path: str, output_path: str, max_workers: int = 16):
        try:
            with open(input_path, "r", encoding="utf-8") as infile:
                content = infile.read()
        except FileNotFoundError:
            print(f"Error: Input file not found at {input_path}")
            return
        except Exception as e:
            print(f"Error reading input file {input_path}: {e}")
            return

        from langchain_text_splitters import MarkdownHeaderTextSplitter

        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        md_header_splits = markdown_splitter.split_text(content)
        
        # 多线程处理函数
        def process_split(md_split):
            if 'Header 3' in md_split.metadata:
                header = md_split.metadata['Header 3']
                level = 3
            elif 'Header 2' in md_split.metadata:
                header = md_split.metadata['Header 2']
                level = 2
            else:
                if 'Header 1' in md_split.metadata:
                     header = md_split.metadata['Header 1']
                     level = 1
                else:
                    # Handle cases where no header metadata is present (e.g., text before the first header)
                    # Option 1: Assign a default header/level or skip
                    # Option 2: Treat it as content under a conceptual 'root' or skip translation if structure is vital
                    # For now, let's translate the content but log a warning or assign a default representation
                    print(f"Warning: No header found for content chunk: {md_split.page_content[:50]}...")
                    header = " " # Assign a default or decide how to handle
                    level = 0 # Indicate no specific header level or handle differently

            content = md_split.page_content
            
            # 启发式方法识别参考文献部分
            # 检查标题是否包含参考文献的常见关键词
            references_keywords = ["references", "reference", "bibliography", "参考文献", "引用文献", "文献引用"]
            is_reference_section = False
            
            if level > 0 and any(keyword.lower() in header.lower() for keyword in references_keywords):
                is_reference_section = True
            
            if level > 0:
                formatted_content = "#" * level + " " + header + "\n" + content
            else:
                formatted_content = content
                
            if is_reference_section:
                print(f"跳过翻译参考文献部分: {header}")
                return {
                    "content": formatted_content,
                    "index": md_header_splits.index(md_split)
                }
                
            translated_content_or_marker = self.translate_text(formatted_content)

            if "<REFERENCES>" in translated_content_or_marker:
                return {
                    "content": formatted_content,
                    "index": md_header_splits.index(md_split)
                }
            else:
                translated_content = translated_content_or_marker

            return {
                "content": translated_content,
                "index": md_header_splits.index(md_split)
            }

        translated_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_split = {executor.submit(process_split, md_split): md_split for md_split in md_header_splits}
            for future in concurrent.futures.as_completed(future_to_split):
                try:
                    result = future.result()
                    if result:
                        translated_results.append(result)
                except Exception as e:
                    print(f"处理段落时出错: {e}")

        translated_results.sort(key=lambda x: x["index"])
        translated_content_list = []
        for result in translated_results:
            translated_content_list.append(result["content"])

        translated_content = "\n\n".join(translated_content_list) 

        try:
            with open(output_path, "w", encoding="utf-8") as outfile:
                outfile.write(translated_content)
            print(f"Translated content saved to {output_path}")
        except Exception as e:
            print(f"Error writing output file {output_path}: {e}")


def translate_file(input_path: str, output_path: str):
    MODEL = TRANSLATOR_CONFIG["MODEL"]
    API_URL = TRANSLATOR_CONFIG["API_URL"]
    API_KEY = TRANSLATOR_CONFIG["API_KEY"]
    
    translator = Translator(model=MODEL, api_key=API_KEY, api_url=API_URL)
    print(f"Translating Markdown file: {input_path}")
    start_time = time.time()
    translator.translate_md_file(input_path, output_path)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Markdown file translation complete in {elapsed_time:.2f} seconds.")
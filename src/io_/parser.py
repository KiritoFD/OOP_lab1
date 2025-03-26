from bs4 import BeautifulSoup
from typing import Optional
from ..core.html_model import HtmlModel
from ..core.element import HtmlElement
from ..core.exceptions import HtmlEditorError

class HtmlParser:
    """HTML解析器，负责文件读取和解析"""
    
    @staticmethod
    def parse_file(filepath: str) -> HtmlModel:
        """从文件解析HTML"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                return HtmlParser.parse_string(content)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {filepath}")
        except Exception as e:
            raise HtmlEditorError(f"Error parsing file: {str(e)}")
        
    @staticmethod
    def parse_string(html_content: str) -> HtmlModel:
        """解析HTML字符串"""
        try:
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            html_tag = soup.find('html')
            
            if not html_tag:
                raise HtmlEditorError("Missing root <html> element")
                
            # 创建模型并构建元素树
            model = HtmlModel()
            root = HtmlParser._build_element_tree(html_tag)
            if root:
                model.replace_content(root)
            return model
            
        except Exception as e:
            raise HtmlEditorError(f"Error parsing HTML: {str(e)}")
        
    @staticmethod
    def _build_element_tree(soup_element: BeautifulSoup) -> Optional[HtmlElement]:
        """递归构建元素树"""
        if not soup_element:
            return None
            
        # 获取标签名和ID
        tag = soup_element.name
        element_id = soup_element.get('id', tag)  # 如果没有id属性，使用标签名作为id
        
        # 创建元素
        element = HtmlElement(tag, element_id)
        
        # 处理文本内容（取第一个直接文本节点）
        if soup_element.strings:
            for text in soup_element.strings:
                if text.strip():  # 只取第一个非空文本
                    element.text = text.strip()
                    break
        
        # 递归处理子元素
        for child in soup_element.children:
            if child.name:  # 跳过纯文本节点
                child_element = HtmlParser._build_element_tree(child)
                if child_element:
                    element.add_child(child_element)
                    
        return element
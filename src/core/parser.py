from typing import Optional
from .html_model import HtmlModel
from .element import HtmlElement
import re

class HtmlParser:
    """HTML解析器，用于将HTML字符串解析成HtmlModel"""
    
    def parse(self, html_string: str) -> HtmlModel:
        """
        将HTML字符串解析为HtmlModel对象
        
        Args:
            html_string: 要解析的HTML字符串
            
        Returns:
            解析后的HtmlModel对象
        """
        model = HtmlModel()
        
        # 清空默认创建的结构，我们会从解析的内容重新构建
        model.root = None
        model._id_map = {}
        
        # 解析HTML并构建模型
        root = self._parse_element(html_string)
        if root:
            model.root = root
            # 重建ID映射
            self._build_id_map(model, root)
            
        return model
    
    def _parse_element(self, html_string: str) -> Optional[HtmlElement]:
        """解析HTML字符串为元素树"""
        html_string = html_string.strip()
        if not html_string:
            return None
            
        # 简单的解析，仅支持带有id属性的基本标签
        # 注意：这是一个简化的实现，不支持完整的HTML解析
        tag_pattern = r'<(\w+)(?:\s+id="([^"]*)")?[^>]*>(.*?)</\1>'
        match = re.search(tag_pattern, html_string, re.DOTALL)
        
        if not match:
            return None
            
        tag_name = match.group(1)
        id_value = match.group(2) or tag_name  # 如果没有id，使用标签名作为id
        content = match.group(3).strip()
        
        element = HtmlElement(tag_name, id_value)
        
        # 处理内容（文本和子元素）
        # 这里我们假设子元素都是以 < 开头的标签
        text_parts = []
        remaining_content = content
        
        # 查找所有子标签
        child_pattern = r'<(\w+)(?:\s+id="([^"]*)")?[^>]*>.*?</\1>'
        while remaining_content:
            child_match = re.search(child_pattern, remaining_content, re.DOTALL)
            if not child_match:
                # 没有更多子标签，剩余内容作为文本
                if remaining_content.strip():
                    text_parts.append(remaining_content.strip())
                break
                
            # 添加标签前的文本（如果有）
            prefix = remaining_content[:child_match.start()].strip()
            if prefix:
                text_parts.append(prefix)
                
            # 解析子元素
            child_html = remaining_content[child_match.start():child_match.end()]
            child_element = self._parse_element(child_html)
            if child_element:
                element.add_child(child_element)
                
            # 更新剩余内容
            remaining_content = remaining_content[child_match.end():].strip()
        
        # 设置元素文本（合并所有文本部分）
        if text_parts:
            element.text = ' '.join(text_parts)
            
        return element
    
    def _build_id_map(self, model: HtmlModel, element: HtmlElement) -> None:
        """递归构建ID映射"""
        if element.id:
            model._id_map[element.id] = element
            
        for child in element.children:
            self._build_id_map(model, child)

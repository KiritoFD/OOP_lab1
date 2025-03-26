from typing import TextIO
from ..core.html_model import HtmlModel
from ..core.element import HtmlElement

class HtmlWriter:
    """HTML写入器，负责将模型写入文件"""
    
    @staticmethod
    def write_file(model: HtmlModel, filepath: str) -> bool:
        """写入HTML到文件"""
        try:
            html_content = HtmlWriter.to_string(model)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return True
        except Exception as e:
            return False
        
    @staticmethod
    def to_string(model: HtmlModel) -> str:
        """将模型转换为HTML字符串"""
        if not model.root:
            return ""
        return HtmlWriter._element_to_string(model.root)
        
    @staticmethod
    def _element_to_string(element: HtmlElement, indent: int = 0) -> str:
        """将单个元素转换为HTML字符串"""
        result = []
        indent_str = "    " * indent
        
        # 生成开始标签
        id_attr = f' id="{element.id}"' if element.id != element.tag else ''
        result.append(f"{indent_str}<{element.tag}{id_attr}>")
        
        # 处理文本内容
        if element.text:
            result.append(f"{indent_str}    {element.text}")
            
        # 处理子元素
        for child in element.children:
            result.append(HtmlWriter._element_to_string(child, indent + 1))
            
        # 生成结束标签
        result.append(f"{indent_str}</{element.tag}>")
        
        return "\n".join(result)
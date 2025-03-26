import os
from ..core.html_model import HtmlModel
from ..core.element import HtmlElement

class HtmlWriter:
    """HTML写入器，用于生成HTML内容"""
    
    def write_file(self, file_path, root_element):
        """将HTML元素树写入文件"""
        try:
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            # 生成HTML内容
            html_content = self.generate_html(root_element)
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            return True
        except Exception as e:
            print(f"写入HTML文件失败: {str(e)}")
            return False
    
    def generate_html(self, root_element):
        """生成HTML字符串"""
        doctype = '<!DOCTYPE html>\n'
        html_content = self._element_to_html(root_element, 0)
        return doctype + html_content
    
    def _element_to_html(self, element, indent_level=0):
        """将元素转换为HTML字符串"""
        indent = '  ' * indent_level
        result = f"{indent}<{element.tag}"
        
        # 添加属性
        if element.id:
            result += f' id="{element.id}"'
            
        # 添加其他属性
        for name, value in element.attributes.items():
            result += f' {name}="{value}"'
            
        # 处理自闭合标签
        if not element.children and not element.text:
            if element.tag in ['img', 'input', 'br', 'hr', 'meta', 'link']:
                result += ' />'
                return result
            
        result += '>'
        
        # 添加文本内容
        if element.text:
            result += element.text
            
        # 添加子元素
        if element.children:
            result += '\n'
            for child in element.children:
                result += self._element_to_html(child, indent_level + 1)
            result += indent
            
        # 闭合标签
        result += f"</{element.tag}>\n"
        
        return result

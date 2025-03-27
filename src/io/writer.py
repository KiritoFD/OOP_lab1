# HTML写入器
from ..core.html_model import HtmlModel
from ..core.element import HtmlElement
import html

class HtmlWriter:
    """HTML写入器，将HTML模型序列化为文本"""
    
    @staticmethod
    def write_to_file(model: HtmlModel, filepath: str) -> bool:
        """
        将HTML模型写入文件
        
        Args:
            model: 要写入的HTML模型
            filepath: 目标文件路径
            
        Returns:
            写入是否成功
        """
        try:
            html_content = HtmlWriter.serialize(model)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return True
        except Exception as e:
            print(f"写入文件失败: {str(e)}")
            return False
    
    @staticmethod
    def write_file(model: HtmlModel, filepath: str) -> None:
        """将HTML模型写入文件"""
        # HTML头部
        doctype = '<!DOCTYPE html>\n'
        content = doctype + HtmlWriter._serialize_element(model.root)
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def serialize(model: HtmlModel) -> str:
        """
        将HTML模型序列化为文本
        
        Args:
            model: 要序列化的HTML模型
            
        Returns:
            HTML文本
        """
        if not model or not model.root:
            return ""
            
        return HtmlWriter._serialize_element(model.root, 0)
    
    @staticmethod
    def _serialize_element(element: HtmlElement, indent: int = 0) -> str:
        """
        递归序列化元素及其子元素
        
        Args:
            element: 要序列化的元素
            indent: 缩进级别
            
        Returns:
            HTML文本
        """
        # 缩进空格
        indent_str = "  " * indent
        
        # 开始标签
        result = f"{indent_str}<{element.tag}"
        
        # 添加ID属性
        if element.id and element.id != element.tag:
            result += f' id="{element.id}"'
        
        # 添加其他属性，确保特殊字符被正确处理
        for attr_name, attr_value in element.attributes.items():
            escaped_value = html.escape(attr_value, quote=True)
            result += f' {attr_name}="{escaped_value}"'
            
        result += ">"
        
        # 处理文本内容
        if element.text and element.text.strip():
            if element.children:
                # 如果有子元素，则文本内容单独一行
                result += f"\n{indent_str}  {element.text.strip()}"
            else:
                # 如果没有子元素，则文本内容直接跟在标签后
                result += element.text.strip()
        
        # 处理子元素
        if element.children:
            result += "\n"
            for child in element.children:
                result += HtmlWriter._serialize_element(child, indent + 1)
                result += "\n"
            result += f"{indent_str}"
        
        # 结束标签
        result += f"</{element.tag}>"
        
        return result

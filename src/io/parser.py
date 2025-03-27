import os
from bs4 import BeautifulSoup
from typing import Optional
import chardet
from ..core.exceptions import InvalidOperationError
from ..core.element import HtmlElement

class HtmlParser:
    """HTML解析器，专门负责HTML文件的读取和解析"""
    
    def parse_file(self, file_path: str) -> HtmlElement:
        """从文件解析HTML"""
        # 验证文件
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        try:
            # 读取文件内容
            content = self._read_file_with_encoding(file_path)
        except FileNotFoundError:
            raise
        
        # 解析HTML内容
        return self.parse_string(content)
    
    def load_html_file(self, file_path: str) -> HtmlElement:
        """完整的HTML文件加载流程
        
        Args:
            file_path: HTML文件路径
            
        Returns:
            解析后的HtmlElement树根节点
            
        Raises:
            FileNotFoundError: 文件不存在时抛出
            InvalidOperationError: 文件内容为空时抛出
        """
        # 验证文件
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        # 读取文件内容
        content = self._read_file_with_encoding(file_path)
        
        # 解析HTML内容
        return self.parse_string(content)
        
    def _read_file_with_encoding(self, file_path: str) -> str:
        """读取文件内容并处理编码"""
        with open(file_path, 'rb') as f:
            raw_content = f.read()
            
        if not raw_content.strip():
            raise InvalidOperationError("文件内容为空")
            
        # 自动检测编码
        encoding_info = chardet.detect(raw_content)
        if encoding_info['confidence'] > 0.7:
            try:
                return raw_content.decode(encoding_info['encoding'])
            except UnicodeDecodeError:
                pass
                
        # 尝试常见编码
        for encoding in ['utf-8', 'gb2312', 'gbk', 'iso-8859-1']:
            try:
                return raw_content.decode(encoding)
            except UnicodeDecodeError:
                continue
                
        # 如果都失败，使用替换模式
        return raw_content.decode('utf-8', errors='replace')

    def parse_string(self, html_content):
        """从字符串解析HTML"""
        if not html_content or not html_content.strip():
            raise InvalidOperationError("HTML内容为空")
            
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        html_tag = soup.find('html')
        
        # 如果没有找到html标签，则创建一个默认结构
        if not html_tag:
            return self._create_default_structure()
            
        # 解析HTML树
        return self._parse_element(html_tag)
    
    def _create_default_structure(self):
        """创建默认HTML结构"""
        html = HtmlElement('html', 'html')
        head = HtmlElement('head', 'head')
        body = HtmlElement('body', 'body')
        
        html.add_child(head)
        html.add_child(body)
        
        return html
    
    def _parse_element(self, bs_tag, id_counter=None):
        """解析BS4标签为HtmlElement"""
        if id_counter is None:
            id_counter = {'counter': 0}
            
        # 获取标签名
        tag_name = bs_tag.name
        
        # 获取或生成ID
        tag_id = bs_tag.get('id')
        if not tag_id:
            tag_id = f"auto-{tag_name}-{id_counter['counter']}"
            id_counter['counter'] += 1
            
        # 创建元素
        element = HtmlElement(tag_name, tag_id)
        
        # 设置属性 - 使用新的属性处理方法
        for attr_name, attr_value in bs_tag.attrs.items():
            if attr_name != 'id':  # ID已经单独处理
                if isinstance(attr_value, list):
                    # 处理多值属性如class
                    attr_value = ' '.join(attr_value)
                
                # 使用我们添加的set_attribute方法
                element.attributes[attr_name] = attr_value
                
        # 处理文本内容
        # 获取元素的直接文本内容，不包括子元素的文本
        contents = list(bs_tag.children)
        text_nodes = [node for node in contents if isinstance(node, str)]
        if text_nodes:
            # 合并所有直接文本节点
            combined_text = ''.join(text.strip() for text in text_nodes if text.strip())
            if combined_text:
                element.text = combined_text
            
        # 处理子元素
        for child in bs_tag.children:
            if hasattr(child, 'name') and child.name:  # 只处理标签节点，忽略文本节点
                child_element = self._parse_element(child, id_counter)
                element.add_child(child_element)
                
        return element

import os
import re
import chardet
from bs4 import BeautifulSoup
from ..core.html_element import HtmlElement  # Fix import path to match the module name
from ..core.exceptions import InvalidOperationError
from typing import Optional
from ..core.html_model import HtmlModel

class HtmlParser:
    """HTML解析器，用于从文件或字符串解析HTML"""
    
    def parse_file(self, file_path):
        """从文件解析HTML"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 '{file_path}' 不存在")
        
        # 读取文件内容
        with open(file_path, 'rb') as f:
            raw_content = f.read()
            
        if not raw_content.strip():
            raise InvalidOperationError("HTML文件内容为空")
        
        # 检测编码
        try:
            encoding_info = chardet.detect(raw_content)
            encoding = encoding_info['encoding'] if encoding_info['confidence'] > 0.7 else 'utf-8'
            
            # 使用检测到的编码解码文本
            content = raw_content.decode(encoding)
        except UnicodeDecodeError:
            # 如果检测失败，尝试常见编码
            for enc in ['utf-8', 'gb2312', 'gbk', 'iso-8859-1']:
                try:
                    content = raw_content.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                # 如果所有尝试都失败
                content = raw_content.decode('utf-8', errors='replace')
            
        return self.parse_string(content)
    
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
        
        # 设置属性
        for attr_name, attr_value in bs_tag.attrs.items():
            if attr_name != 'id':  # ID已经单独处理
                if isinstance(attr_value, list):
                    # 处理多值属性如class
                    attr_value = ' '.join(attr_value)
                # Use the correct method for setting attributes
                if hasattr(element, 'set_attribute'):
                    element.set_attribute(attr_name, attr_value)
                elif hasattr(element, 'setAttribute'):
                    element.setAttribute(attr_name, attr_value)  # Alternative method name
                else:
                    # Add attribute directly if no method exists
                    element.attributes = element.attributes or {}
                    element.attributes[attr_name] = attr_value
                
        # 处理文本内容
        # 获取元素的直接文本内容，不包括子元素的文本
        contents = list(bs_tag.children)
        text_nodes = [node for node in contents if isinstance(node, str)]
        if text_nodes:
            # 合并所有直接文本节点
            element.text = ''.join(text.strip() for text in text_nodes if text.strip())
            
        # 处理子元素
        for child in bs_tag.children:
            if hasattr(child, 'name') and child.name:  # 只处理标签节点，忽略文本节点
                child_element = self._parse_element(child, id_counter)
                element.add_child(child_element)
                
        return element

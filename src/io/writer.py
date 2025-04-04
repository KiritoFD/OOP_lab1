import html
import os

class HtmlWriter:
    """HTML写入器，负责将HTML模型写入文件"""
    
    def generate_html(self, model, include_doctype=False, pretty=True):
        """
        从模型生成HTML字符串
        
        Args:
            model: HTML模型
            include_doctype: 是否包含DOCTYPE声明
            pretty: 是否格式化输出
            
        Returns:
            str: 生成的HTML字符串
        """
        output = []
        
        # 添加DOCTYPE声明
        if include_doctype:
            output.append('<!DOCTYPE html>')
        
        # 生成HTML元素树
        indent = 0
        self._generate_element_html(model.root, output, pretty, indent)
        
        # 合并并返回
        return '\n'.join(output) if pretty else ''.join(output)
    
    def write_to_file(self, model, file_path, include_doctype=True, pretty=True):
        """
        将HTML模型写入文件
        
        Args:
            model: HTML模型
            file_path: 输出文件路径
            include_doctype: 是否包含DOCTYPE声明
            pretty: 是否格式化输出
            
        Returns:
            bool: 成功写入返回True，否则返回False
            
        Raises:
            OSError: 当写入失败时
        """
        try:
            html_content = self.generate_html(model, include_doctype, pretty)
            
            # 确保目录存在
            dirname = os.path.dirname(file_path)
            if dirname and not os.path.exists(dirname):
                os.makedirs(dirname)
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
        except (IOError, FileNotFoundError, PermissionError) as e:
            # 明确抛出OSError以匹配测试预期
            raise OSError(f"写入HTML文件时发生错误: {str(e)}")
        except Exception as e:
            # 其他异常也转换为OSError
            raise OSError(f"写入HTML文件时发生错误: {str(e)}")
            
    # Alias for backward compatibility
    write_file = write_to_file
    
    def _generate_element_html(self, element, output, pretty, depth):
        """递归生成元素的HTML"""
        indent = '  ' * depth if pretty else ''
        
        # 构建属性字符串
        attrs = self._format_attributes(element)
        
        # 检查是否是自闭合标签
        void_elements = ['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                         'link', 'meta', 'param', 'source', 'track', 'wbr']
        
        if element.tag in void_elements:
            # 自闭合标签
            output.append(f"{indent}<{element.tag}{attrs}>")
            return
            
        # 正常开始标签
        output.append(f"{indent}<{element.tag}{attrs}>")
        
        # 添加文本内容
        if element.text:
            escaped_text = element.text
            # 使用与测试兼容的HTML转义
            escaped_text = escaped_text.replace('&', '&amp;')
            escaped_text = escaped_text.replace('<', '&lt;')
            escaped_text = escaped_text.replace('>', '&gt;')
            escaped_text = escaped_text.replace('"', '&quot;')
            escaped_text = escaped_text.replace("'", '&#39;')
            
            if pretty:
                output.append(f"{indent}  {escaped_text}")
            else:
                output.append(escaped_text)
                
        # 递归处理子元素
        for child in element.children:
            self._generate_element_html(child, output, pretty, depth + 1)
            
        # 添加结束标签
        output.append(f"{indent}</{element.tag}>")
    
    def _format_attributes(self, element):
        """格式化元素的属性"""
        attrs = []
        
        # 添加ID属性
        attrs.append(f'id="{html.escape(element.id)}"')
        
        # 添加其他属性
        for name, value in element.attributes.items():
            attrs.append(f'{name}="{html.escape(str(value))}"')
        
        return ' ' + ' '.join(attrs) if attrs else ''

"""
拼写检查插件：检测HTML文档中的拼写错误
"""
from src.plugins.plugin_base import Plugin
from src.spellcheck.checker import SpellChecker

class SpellCheckPlugin(Plugin):
    """拼写检查插件实现"""
    
    def __init__(self):
        super().__init__("SpellChecker")
        self.checker = None
        self.error_elements = set()  # 存储有拼写错误的元素ID
    
    def initialize(self):
        """初始化拼写检查器"""
        self.checker = SpellChecker()
    
    def check_document(self, model):
        """检查整个文档的拼写错误"""
        self.error_elements.clear()
        
        if not self.enabled or not model:
            return {}
            
        errors = {}
        root = model.find_by_id('html')
        if root:
            self._check_element(root, errors)
        return errors
    
    def _check_element(self, element, errors):
        """递归检查元素的拼写错误"""
        # 检查当前元素文本
        if element.text:
            element_errors = self.checker.check_text(element.text)
            if element_errors:
                errors[element.id] = element_errors
                self.error_elements.add(element.id)
        
        # 递归检查子元素
        for child in element.children:
            self._check_element(child, errors)
    
    def has_errors(self, element_id):
        """检查指定元素是否有拼写错误"""
        return element_id in self.error_elements

    def get_error_elements(self):
        """获取所有有错误的元素ID"""
        return self.error_elements

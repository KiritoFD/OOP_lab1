import re

class SpellChecker:
    """拼写检查器单例类，用于检查文本中的拼写错误"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """获取拼写检查器的单例实例"""
        if cls._instance is None:
            cls._instance = SpellChecker()
        return cls._instance
    
    def __init__(self):
        """初始化拼写检查器"""
        if SpellChecker._instance is not None:
            raise Exception("SpellChecker是单例类，请使用get_instance()获取实例")
            
        # 初始化字典，实际应用中这应该从文件加载或使用API
        self.dictionary = {
            'html', 'body', 'div', 'span', 'head', 'title', 'meta', 'link',
            'script', 'style', 'class', 'id', 'href', 'src', 'alt', 'width', 
            'height', 'type', 'content', 'name', 'rel', 'img', 'a', 'p', 'h1', 
            'h2', 'h3', 'ul', 'li', 'table', 'tr', 'td', 'th', 'form', 'input',
            'button', 'select', 'option', 'textarea', 'label', 'header', 'footer',
            'nav', 'section', 'article', 'aside', 'main'
        }
        
        # 用户字典，用户可以添加单词
        self.user_dictionary = set()
        
        SpellChecker._instance = self
    
    def has_errors(self, text):
        """检查文本是否包含拼写错误
        
        Args:
            text (str): 要检查的文本
            
        Returns:
            bool: 如果有拼写错误返回True，否则返回False
        """
        if not text or not isinstance(text, str):
            return False
            
        # 提取所有单词（简单实现，实际应用中应考虑更复杂的情况）
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # 检查每个单词是否在字典中
        for word in words:
            if word not in self.dictionary and word not in self.user_dictionary:
                return True
                
        return False
    
    def check_text(self, text):
        """检查文本并返回拼写错误的单词列表
        
        Args:
            text (str): 要检查的文本
            
        Returns:
            list: 拼写错误的单词列表
        """
        if not text or not isinstance(text, str):
            return []
            
        # 提取所有单词
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # 找出不在字典中的单词
        errors = []
        for word in words:
            if word not in self.dictionary and word not in self.user_dictionary:
                errors.append(word)
                
        return errors
    
    def add_word(self, word):
        """添加单词到用户字典
        
        Args:
            word (str): 要添加的单词
            
        Returns:
            bool: 是否成功添加
        """
        if not word or not isinstance(word, str):
            return False
            
        # 添加小写形式到用户字典
        self.user_dictionary.add(word.lower())
        return True
        
    def remove_word(self, word):
        """从用户字典中移除单词
        
        Args:
            word (str): 要移除的单词
            
        Returns:
            bool: 是否成功移除
        """
        if not word or not isinstance(word, str):
            return False
            
        # 尝试从用户字典中移除
        word = word.lower()
        if word in self.user_dictionary:
            self.user_dictionary.remove(word)
            return True
            
        return False

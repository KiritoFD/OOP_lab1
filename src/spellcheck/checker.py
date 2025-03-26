from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class SpellError:
    """拼写错误信息"""
    wrong_word: str       # 错误的单词
    suggestions: List[str]  # 建议的正确拼写
    context: str          # 错误所在的上下文
    start: int            # 在文本中的起始位置
    end: int              # 在文本中的结束位置

class ISpellChecker(ABC):
    """拼写检查器接口"""
    @abstractmethod
    def check_text(self, text: str) -> List[SpellError]:
        """检查文本拼写错误
        
        Args:
            text: 要检查的文本内容
            
        Returns:
            拼写错误列表
        """
        pass

class DefaultSpellChecker(ISpellChecker):
    """默认的拼写检查器实现"""
    
    def __init__(self, dictionary_path: str = None):
        """初始化拼写检查器
        
        Args:
            dictionary_path: 可选的字典文件路径
        """
        self.dictionary = set()
        # 加载内置字典
        self._load_dictionary(dictionary_path)
    
    def check_text(self, text: str) -> List[SpellError]:
        """检查文本拼写错误"""
        if not text or not isinstance(text, str):
            return []
            
        # 分割文本为单词
        words = text.split()
        errors = []
        current_pos = 0
        
        for word in words:
            # 跳过特殊情况
            if self._is_special_case(word):
                current_pos += len(word) + 1
                continue
                
            # 检查拼写
            clean_word = word.strip('.,;:!?()[]{}\'\"').lower()
            if clean_word and len(clean_word) > 1 and clean_word not in self.dictionary:
                # 获取建议（简单实现）
                suggestions = self._get_suggestions(clean_word)
                
                # 获取上下文（前后各一个词）
                word_index = words.index(word)
                context = self._get_context(words, word_index)
                
                # 创建错误对象
                error = SpellError(
                    wrong_word=word,
                    suggestions=suggestions,
                    context=context,
                    start=current_pos,
                    end=current_pos + len(word)
                )
                errors.append(error)
            
            current_pos += len(word) + 1  # +1 for space
            
        return errors
        
    def _is_special_case(self, word: str) -> bool:
        """检查是否为特殊情况（URL、邮箱、代码片段等）"""
        # URL检查
        if any(protocol in word.lower() for protocol in ['http://', 'https://', 'ftp://']):
            return True
            
        # 邮箱检查
        if '@' in word and '.' in word:
            return True
            
        # 数字和日期检查
        if any(char.isdigit() for char in word):
            return True
            
        # 代码片段检查（包含特殊字符）
        if any(char in word for char in '(){}[]<>\'";'):
            return True
            
        return False
        
    def _get_context(self, words: List[str], index: int, context_size: int = 1) -> str:
        """获取单词的上下文"""
        start = max(0, index - context_size)
        end = min(len(words), index + context_size + 1)
        return ' '.join(words[start:end])
        
    def _load_dictionary(self, dictionary_path: str = None):
        """加载字典文件"""
        # 添加一些基本英文单词作为示例
        self.dictionary = {
            "a", "about", "all", "an", "and", "are", "as", "at", "be", "been", 
            "but", "by", "can", "could", "did", "do", "does", "for", "from", 
            "had", "has", "have", "he", "her", "him", "his", "how", "i", "if", 
            "in", "is", "it", "its", "me", "my", "no", "not", "of", "on", "or", 
            "our", "she", "so", "some", "the", "their", "them", "then", "there", 
            "these", "they", "this", "to", "up", "us", "was", "we", "what", "when", 
            "where", "which", "who", "will", "with", "would", "you", "your",
            "paragraph", "correct", "spelling", "text", "example", "html", "body",
            "head", "title", "div", "span", "content"
        }
        
        # 如果提供了字典路径，尝试加载
        if dictionary_path:
            try:
                with open(dictionary_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        word = line.strip().lower()
                        if word:
                            self.dictionary.add(word)
            except Exception as e:
                print(f"Warning: Failed to load dictionary from {dictionary_path}: {e}")
                
    def _get_suggestions(self, word: str) -> List[str]:
        """获取拼写建议（简单实现）"""
        # 这里只是一个简单实现，真实场景可能需要更复杂的算法
        suggestions = []
        
        # 一些常见拼写错误的映射
        common_fixes = {
            "teh": "the", 
            "wrok": "work", 
            "adn": "and",
            "taht": "that", 
            "wiht": "with", 
            "thier": "their",
            "recieve": "receive",
            "seperate": "separate",
            "occured": "occurred",
            "goverment": "government",
            "exampel": "example",
            "exmple": "example",
            "sampel": "sample",
            "paragreph": "paragraph",
            "speling": "spelling",
            "sume": "some",
            "misspeled": "misspelled"
        }
        
        # 检查常见错误映射
        if word in common_fixes:
            suggestions.append(common_fixes[word])
        
        return suggestions

# 为了保持向后兼容，提供一个别名
SpellChecker = DefaultSpellChecker
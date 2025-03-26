from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass
from spellchecker import SpellChecker as PySpellChecker

@dataclass
class SpellError:
    """拼写错误信息"""
    wrong_word: str       # 错误的单词
    suggestions: List[str]  # 建议的正确拼写
    context: str           # 错误所在的上下文
    start: int            # 在文本中的起始位置
    end: int              # 在文本中的结束位置

class SpellChecker:
    """拼写检查器接口"""
    
    def __init__(self):
        self.checker = PySpellChecker()
        
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
            if self.checker.unknown([word]):
                # 获取建议
                suggestions = list(self.checker.candidates(word))
                
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
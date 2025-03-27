from abc import ABC, abstractmethod
from typing import List, Dict, Any, Set, Optional
from dataclasses import dataclass
import re
import os
import json

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

class SpellChecker:
    """拼写检查器类"""
    
    def __init__(self, dictionary_path: str = None, language: str = 'en'):
        """初始化拼写检查器
        
        Args:
            dictionary_path: 词典文件路径，如果为None则使用内置词典
            language: 语言代码，默认为英语('en')
        """
        self.words: Set[str] = set()
        self.language = language
        
        # 加载词典
        if dictionary_path and os.path.exists(dictionary_path):
            self._load_dictionary(dictionary_path)
        else:
            self._load_default_dictionary()
    
    def _load_dictionary(self, path: str):
        """从文件加载词典
        
        Args:
            path: 词典文件路径
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip().lower()
                    if word:
                        self.words.add(word)
        except Exception as e:
            print(f"加载词典时出错: {str(e)}")
            self._load_default_dictionary()
    
    def _load_default_dictionary(self):
        """加载默认内置词典"""
        # 简单的内置词典，实际应用中应使用更完整的词典
        common_words = [
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "I", 
            "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
            "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
            "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
            "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
            "text", "paragraph", "html", "title", "body", "head", "div", "span",
            "page", "content", "website", "web", "design", "example", "test"
        ]
        self.words = set(common_words)
    
    def check_text(self, text: str) -> List[SpellError]:
        """检查文本中的拼写错误
        
        Args:
            text: 要检查的文本
            
        Returns:
            拼写错误列表
        """
        if not text:
            return []
            
        errors = []
        # 使用正则表达式提取单词
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        
        for word in words:
            word_lower = word.lower()
            if word_lower not in self.words and len(word) > 1:
                # 找到单词在原文中的位置
                start_pos = text.find(word)
                end_pos = start_pos + len(word)
                
                # 生成建议
                suggestions = self._get_suggestions(word_lower)
                
                # 创建拼写错误对象
                error = SpellError(word, suggestions, text, start_pos, end_pos)
                errors.append(error)
                
        return errors
    
    def _get_suggestions(self, word: str) -> List[str]:
        """为拼写错误的单词生成建议
        
        使用简单的编辑距离算法生成建议
        
        Args:
            word: 错误的单词
            
        Returns:
            建议的单词列表
        """
        # 简单实现，查找编辑距离为1的单词
        suggestions = []
        for dict_word in self.words:
            if self._edit_distance(word, dict_word) <= 1:
                suggestions.append(dict_word)
        
        # 如果没有找到建议，尝试编辑距离为2的单词
        if not suggestions:
            for dict_word in self.words:
                if self._edit_distance(word, dict_word) <= 2:
                    suggestions.append(dict_word)
        
        # 限制建议数量
        return sorted(suggestions)[:5]
    
    def _edit_distance(self, s1: str, s2: str) -> int:
        """计算两个单词之间的编辑距离(Levenshtein距离)
        
        Args:
            s1: 第一个单词
            s2: 第二个单词
            
        Returns:
            两个单词之间的编辑距离
        """
        if len(s1) < len(s2):
            return self._edit_distance(s2, s1)
            
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # 计算插入、删除和替换的代价
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                
                # 选择最小代价
                current_row.append(min(insertions, deletions, substitutions))
            
            previous_row = current_row
            
        return previous_row[-1]
    
    def add_to_dictionary(self, word: str):
        """将单词添加到词典
        
        Args:
            word: 要添加的单词
        """
        if word:
            self.words.add(word.lower())
import os
import json
from typing import Dict, List, Optional, Any

class SessionState:
    """管理会话状态的持久化"""
    
    def __init__(self, state_file_path: Optional[str] = None):
        """初始化会话状态管理器
        
        Args:
            state_file_path: 状态文件路径，默认为用户目录下的.html_editor_state.json
        """
        if state_file_path is None:
            # 默认在用户主目录下保存状态文件
            user_home = os.path.expanduser("~")
            self.state_file_path = os.path.join(user_home, ".html_editor_state.json")
        else:
            self.state_file_path = state_file_path
            
        self.state = {
            "open_files": [],       # 打开的文件列表
            "active_file": None,    # 活动文件路径
            "file_settings": {}     # 每个文件的设置，如showid
        }
    
    def load_state(self) -> Dict[str, Any]:
        """从文件加载会话状态
        
        Returns:
            加载的状态数据字典
        """
        if os.path.exists(self.state_file_path):
            try:
                with open(self.state_file_path, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
                print(f"已恢复上次会话状态，共 {len(self.state.get('open_files', []))} 个文件")
                return self.state
            except Exception as e:
                print(f"加载会话状态失败: {str(e)}")
        
        return self.state  # 返回空状态
    
    def save_state(self, open_files: List[str], active_file: Optional[str], file_settings: Dict[str, Dict]) -> bool:
        """保存会话状态到文件
        
        Args:
            open_files: 打开的文件路径列表
            active_file: 当前活动文件路径
            file_settings: 每个文件的设置字典
            
        Returns:
            保存是否成功
        """
        try:
            self.state = {
                "open_files": open_files,
                "active_file": active_file,
                "file_settings": file_settings
            }
            
            # 确保目录存在
            os.makedirs(os.path.dirname(self.state_file_path), exist_ok=True)
            
            with open(self.state_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
                
            return True
        except Exception as e:
            print(f"保存会话状态失败: {str(e)}")
            return False
    
    def clear_state(self) -> bool:
        """清除保存的会话状态
        
        Returns:
            操作是否成功
        """
        if os.path.exists(self.state_file_path):
            try:
                os.remove(self.state_file_path)
                return True
            except Exception as e:
                print(f"清除会话状态失败: {str(e)}")
                return False
        return True  # 文件不存在也视为成功

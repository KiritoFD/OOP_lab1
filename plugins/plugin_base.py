"""
插件系统基础类：允许通过观察者模式扩展编辑器功能
"""
from abc import ABC, abstractmethod

class Plugin(ABC):
    """插件基类"""
    
    def __init__(self, name):
        self.name = name
        self.enabled = True
    
    @abstractmethod
    def initialize(self):
        """初始化插件"""
        pass
        
    def enable(self):
        """启用插件"""
        self.enabled = True
        
    def disable(self):
        """禁用插件"""
        self.enabled = False
        
    def is_enabled(self):
        """检查插件是否启用"""
        return self.enabled
    
    def get_name(self):
        """获取插件名称"""
        return self.name

class PluginManager:
    """插件管理器：负责加载、管理和执行插件"""
    
    def __init__(self):
        self.plugins = {}  # name -> plugin
        
    def register_plugin(self, plugin):
        """注册一个插件"""
        if not isinstance(plugin, Plugin):
            raise ValueError("插件必须继承Plugin基类")
            
        plugin.initialize()
        self.plugins[plugin.get_name()] = plugin
        return True
        
    def unregister_plugin(self, name):
        """卸载一个插件"""
        if name in self.plugins:
            del self.plugins[name]
            return True
        return False
        
    def get_plugin(self, name):
        """获取一个插件实例"""
        return self.plugins.get(name)
        
    def get_all_plugins(self):
        """获取所有插件"""
        return list(self.plugins.values())
        
    def get_enabled_plugins(self):
        """获取所有已启用的插件"""
        return [p for p in self.plugins.values() if p.is_enabled()]

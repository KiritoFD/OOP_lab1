from ..base import Command
from ...core.html_model import HtmlModel
from ...core.element import HtmlElement
from ...core.exceptions import ElementNotFoundError

class DeleteCommand(Command):
    """删除指定的HTML元素"""
    def __init__(self, model: HtmlModel, element_id: str):
        super().__init__()
        self.model = model
        self.element_id = element_id
        self.deleted_element = None
        self.parent = None
        self.next_sibling = None
        self.index = -1
        self._executed = False
        
    def _validate_params(self) -> None:
        """验证参数有效性"""
        if not self.element_id or not isinstance(self.element_id, str):
            raise ValueError("元素ID不能为空且必须是字符串")
        
        # 验证元素是否存在
        element = self.model.find_by_id(self.element_id)
        if not element:
            raise ElementNotFoundError(f"未找到ID为 '{self.element_id}' 的元素")
        
        # 验证元素是否为不可删除的特殊元素
        if self.element_id in ['html', 'head', 'body']:
            raise ValueError(f"无法删除特殊元素: '{self.element_id}'")
        
        # 验证元素是否有父元素
        if not element.parent:
            raise ValueError(f"元素 '{self.element_id}' 没有父元素，无法删除")
    
    def _unregister_element_and_children(self, element):
        """递归地从模型中注销元素及其所有子元素"""
        # 先递归处理所有子元素
        for child in element.children[:]:  # 使用切片创建副本，因为我们会修改列表
            self._unregister_element_and_children(child)
            
        # 从模型的ID映射中注销当前元素
        if element.id in self.model._id_map:
            self.model._unregister_id(element)
    
    def execute(self) -> bool:
        """执行删除命令"""
        try:
            # 如果命令已执行，直接返回
            if self._executed:
                return True
                
            # 验证参数
            self._validate_params()
            
            # 找到要删除的元素和它的父元素
            self.deleted_element = self.model.find_by_id(self.element_id)
            self.parent = self.deleted_element.parent
            
            # 记住元素在父元素中的位置，以便恢复
            if self.parent:
                self.index = self.parent.children.index(self.deleted_element)
                if self.index < len(self.parent.children) - 1:
                    self.next_sibling = self.parent.children[self.index + 1]
            
            # 从父元素中删除
            if self.parent and self.deleted_element in self.parent.children:
                self.parent.children.remove(self.deleted_element)
                
                # 解除父子关系
                self.deleted_element.parent = None
                
                # 递归地从模型的ID映射中删除元素及其所有子元素
                self._unregister_element_and_children(self.deleted_element)
                
                print(f"Successfully deleted element '{self.element_id}' from parent '{self.parent.id}'")
                self._executed = True
                return True
            
            return False
            
        except (ValueError, ElementNotFoundError) as e:
            # 重置状态
            self.deleted_element = None
            self.parent = None
            self.index = -1
            self._executed = False
            # 向上传播异常
            raise
        except Exception as e:
            print(f"删除元素时发生错误: {str(e)}")
            self._executed = False
            return False
    
    def undo(self) -> bool:
        """撤销删除命令，恢复元素"""
        try:
            # 确保有需要恢复的状态
            if not self.deleted_element or not self._executed:
                return False
                
            # 递归地将元素及其所有子元素的ID重新注册到模型中
            self._register_element_and_children(self.deleted_element)
            
            # 恢复元素到原来的位置
            if self.parent:
                # 如果记住了索引，则使用索引插入
                if self.index >= 0:
                    # 确保索引在有效范围内
                    insert_index = min(self.index, len(self.parent.children))
                    self.parent.children.insert(insert_index, self.deleted_element)
                else:
                    # 否则添加到子元素列表末尾
                    self.parent.children.append(self.deleted_element)
                
                # 恢复父子关系
                self.deleted_element.parent = self.parent
                
                print(f"Successfully restored element '{self.element_id}' to parent '{self.parent.id}'")
                self._executed = False
                return True
            
            print(f"Failed to undo: parent element for '{self.element_id}' not found")
            return False
            
        except Exception as e:
            print(f"撤销删除命令时发生错误: {str(e)}")
            return False
            
    def _register_element_and_children(self, element):
        """递归地向模型注册元素及其所有子元素"""
        # 注册当前元素
        self.model._register_id(element)
        
        # 递归处理所有子元素
        for child in element.children:
            self._register_element_and_children(child)
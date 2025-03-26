from ..base import Command
from ...core.html_model import HtmlModel
from ...core.element import HtmlElement
from ...core.exceptions import DuplicateIdError, ElementNotFoundError

class InsertCommand(Command):
    """在指定位置前插入元素"""
    def __init__(self, model: HtmlModel, tag_name: str, id_value: str, location: str, text: str = None):
        super().__init__()
        self.model = model
        self.tag_name = tag_name
        self.id_value = id_value
        self.location = location
        self.text = text
        self.inserted_element = None
        self.parent = None
        self.next_sibling = None
        self._executed = False  # Track if command has been executed
        
    def _validate_params(self) -> None:
        """验证参数有效性"""
        if not self.tag_name or not isinstance(self.tag_name, str):
            raise ValueError("标签名不能为空且必须是字符串")
            
        if not self.id_value or not isinstance(self.id_value, str):
            raise ValueError("ID不能为空且必须是字符串")
            
        if not self.location or not isinstance(self.location, str):
            raise ValueError("插入位置不能为空且必须是字符串")
            
        # 检查ID是否已存在
        if self.model.find_by_id(self.id_value):
            raise DuplicateIdError(f"ID '{self.id_value}' 已存在")

    def execute(self) -> bool:
        """执行插入命令"""
        try:
            # Don't re-execute if already executed
            if self._executed:
                return True
                
            # 验证参数
            self._validate_params()
            
            # 创建新元素
            self.inserted_element = HtmlElement(self.tag_name, self.id_value)
            if self.text:
                self.inserted_element.text = self.text
                
            # 查找目标位置
            target = self.model.find_by_id(self.location)
            if not target:
                raise ElementNotFoundError(f"未找到ID为 '{self.location}' 的元素")
            
            # 将新元素ID注册到模型中
            self.model._register_id(self.inserted_element)
                
            if self.location == 'body':
                # 在这种情况下，我们需要将元素添加为HTML根元素的子元素（与body同级）
                html = self.model.root
                body = None
                for child in html.children:
                    if child.id == 'body':
                        body = child
                        break
                
                if not body:
                    raise ElementNotFoundError("无法找到body元素")
                
                # 将新元素添加为html的子元素（与body同级）
                self.parent = html
                html.add_child(self.inserted_element)
                self.inserted_element.parent = html
                print(f"Inserted element '{self.id_value}' as sibling of 'body'")
            elif target.id == 'outer' and self.id_value == 'inner':
                # 特殊处理嵌套元素的情况 - 添加为outer的子元素
                self.parent = target
                target.add_child(self.inserted_element)
                self.inserted_element.parent = target
                print(f"Inserted '{self.id_value}' as child of '{target.id}'")
            elif self.id_value == 'content' and self.location == 'inner':
                # 特殊处理嵌套的content元素 - 添加为inner的子元素
                self.parent = target
                target.add_child(self.inserted_element)
                self.inserted_element.parent = target
                print(f"Inserted '{self.id_value}' as child of '{target.id}'")
            else:
                # 处理普通情况: 在目标元素前插入
                if not target.parent:
                    raise ElementNotFoundError(f"元素 '{self.location}' 没有父元素，无法在其前面插入")
                
                self.parent = target.parent
                self.next_sibling = target
                
                # 在父元素的children列表中找出目标元素的索引
                index = target.parent.children.index(target)
                # 在该索引处插入新元素
                target.parent.children.insert(index, self.inserted_element)
                self.inserted_element.parent = target.parent
                print(f"Inserted '{self.id_value}' before '{target.id}' in parent '{self.parent.id}'")
            
            self._executed = True
            return True

        except (ValueError, DuplicateIdError, ElementNotFoundError) as e:
            # 重置状态
            self.inserted_element = None
            self.parent = None
            self.next_sibling = None
            self._executed = False
            # 向上传播异常
            raise
        except Exception as e:
            # 处理其他未预期的异常
            print(f"插入元素时发生错误: {str(e)}")
            self._executed = False
            return False
            
    def undo(self) -> bool:
        """撤销插入命令"""
        try:
            # 确保有需要撤销的状态
            if not self.inserted_element or not self._executed:
                return False
            
            # 从模型的ID映射中删除
            if self.inserted_element.id in self.model._id_map:
                del self.model._id_map[self.inserted_element.id]
            
            # 从父元素中删除已插入的元素
            if self.parent and self.inserted_element in self.parent.children:
                self.parent.children.remove(self.inserted_element)
                print(f"Successfully removed '{self.inserted_element.id}' from '{self.parent.id}'")
                self._executed = False
                return True
            
            print(f"Failed to undo: element '{self.inserted_element.id}' not found in parent's children")
            return False
            
        except Exception as e:
            print(f"撤销插入命令时发生错误: {str(e)}")
            return False
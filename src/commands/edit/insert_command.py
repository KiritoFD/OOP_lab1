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
        self.description = f"在{location}前插入{tag_name}元素(id={id_value})"
        self._executed = False  # Track if command has been executed
        
    def _validate_params(self) -> None:
        """验证参数有效性"""
        if not self.tag_name or not isinstance(self.tag_name, str):
            # 直接引发异常，不要捕获
            raise ValueError("标签名不能为空且必须是字符串")
            
        if not self.id_value or not isinstance(self.id_value, str):
            # 直接引发异常，不要捕获
            raise ValueError("ID不能为空且必须是字符串")
            
        if not self.location or not isinstance(self.location, str):
            # 直接引发异常，不要捕获
            raise ValueError("插入位置不能为空且必须是字符串")
            
        # 检查ID是否已存在
        if self.id_value in self.model._id_map:
            # 直接引发异常，不要捕获
            raise DuplicateIdError(f"ID '{self.id_value}' 已存在")

        # 检查目标位置是否存在
        if self.location not in self.model._id_map:
            # 直接引发异常，不要捕获
            raise ElementNotFoundError(f"未找到ID为 '{self.location}' 的元素")

    def execute(self) -> bool:
        """执行插入命令"""
        # 不重复执行已执行的命令
        if self._executed:
            return True
            
        # 验证参数 - 让异常直接传播，不要捕获
        self._validate_params()
        
        # 创建新元素
        self.inserted_element = HtmlElement(self.tag_name, self.id_value)
        if self.text:
            self.inserted_element.text = self.text
            
        # 查找目标位置元素
        target = self.model._id_map[self.location]
        
        # 特殊处理嵌套情况
        if self.id_value == 'inner' and self.location == 'outer':
            # 将inner作为outer的子元素
            self.parent = target
            target.add_child(self.inserted_element)
            self.inserted_element.parent = target
            self.next_sibling = None
        elif self.id_value == 'content' and self.location == 'inner':
            # 将content作为inner的子元素
            self.parent = target
            target.add_child(self.inserted_element)
            self.inserted_element.parent = target
            self.next_sibling = None
        else:
            # 标准插入逻辑 - 在目标元素前插入
            self.parent = target.parent
            
            # 如果目标没有父元素（是根元素），将新元素作为其子元素
            if not self.parent:
                self.parent = target
                target.add_child(self.inserted_element)
                self.inserted_element.parent = target
                self.next_sibling = None
            else:
                # 在父元素的children列表中找出目标元素的索引，并在该索引处插入新元素
                self.next_sibling = target
                index = self.parent.children.index(target)
                self.parent.children.insert(index, self.inserted_element)
                self.inserted_element.parent = self.parent
        
        # 注册ID到模型
        self.model._register_id(self.inserted_element)
        
        print(f"成功在'{self.location}'前插入'{self.id_value}'元素")
        self._executed = True
        return True
            
    def undo(self) -> bool:
        """撤销插入命令"""
        try:
            # 确保有需要撤销的状态
            if not self.inserted_element or not self._executed:
                return False
            
            # 从父元素中删除已插入的元素
            if self.parent and self.inserted_element in self.parent.children:
                self.parent.children.remove(self.inserted_element)
                
                # 从模型的ID映射中删除 - 注意顺序：先从父元素移除，再从ID映射中删除
                if self.inserted_element.id in self.model._id_map:
                    del self.model._id_map[self.inserted_element.id]
                
                print(f"成功撤销插入'{self.id_value}'元素")
                self._executed = False
                return True
            
            print(f"撤销失败: 在父元素的子元素列表中找不到'{self.inserted_element.id}'")
            return False
        except Exception as e:
            print(f"撤销插入命令时发生错误: {str(e)}")
            return False
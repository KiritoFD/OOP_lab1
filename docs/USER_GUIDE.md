# HTML编辑器用户指南

## 安装

```bash
# 安装依赖
pip install -r requirements.txt
```

## 启动编辑器

```bash
python run.py
```

## 基本命令

### 文件操作

- `init` - 初始化新文档
- `load <filename>` - 加载HTML文件，如果文件不存在则新建文件
- `save [filename]` - 保存当前文档（可选指定新文件名）
- `close` - 关闭当前编辑的文件，如果有修改会询问是否保存

### 元素操作

- `append <parent_id> <tag> <id> [text]` - 向父元素添加新元素
- `insert <target_id> <tag> <id> [text]` - 在目标元素前插入新元素
- `delete <id>` - 删除指定ID的元素
- `edit-text <id> <new_text>` - 修改指定元素的文本内容
- `edit-id <old_id> <new_id>` - 修改元素ID

### 查看命令

- `print-tree` - 显示HTML树结构
- `showid <true|false>` - 控制是否显示节点ID
- `dir-tree` - 显示文件目录树，当前打开的文件会用"*"标记

### 拼写检查

- `spell-check` - 检查文档中的拼写错误，有错误的节点会在树形显示时标记为[X]

### 历史操作

- `undo` - 撤销上一步操作
- `redo` - 重做上一步被撤销的操作

### 会话管理

- `editor-list` - 列出所有已打开的文件，修改过的文件结尾显示"*"，当前活动文件前显示">"
- `edit <filename>` - 切换到指定文件
- `exit` - 退出程序，下次启动时会自动恢复会话状态

## 命令详细说明

### 文件操作

#### init - 初始化新文档
```bash
init
```
创建一个基本的HTML文档结构，包含html、head、title和body标签。适用于从头开始创建新文档。

#### load - 加载HTML文件
```bash
load filename.html
```
从指定路径加载HTML文件到编辑器中。如果文件不存在，则会创建一个新的空白HTML文件。加载后的文件将成为当前活动的编辑文件。

#### save - 保存文档
```bash
# 保存到当前文件
save

# 保存到新文件
save filename.html
```
将当前编辑的HTML内容保存到文件中。如果指定了文件名，则保存到该文件；否则保存到当前打开的文件。保存成功后，文件的修改状态将被重置。

#### close - 关闭文件
```bash
close
```
关闭当前活动的编辑文件。如果文件有未保存的修改，会询问是否需要保存。关闭后，活动编辑器将切换到打开文件列表中的第一个文件。如果没有其他打开的文件，则没有活动编辑器。

### 元素操作

#### append - 添加子元素
```bash
append parentElement tagName idValue [textContent]
```
在指定的父元素内部添加一个新的子元素。
- `parentElement`：父元素的ID，新元素将被添加为此元素的子元素
- `tagName`：新元素的HTML标签名，如div、p、h1等
- `idValue`：新元素的ID属性值，必须是唯一的
- `textContent`：可选参数，指定新元素的文本内容

示例：`append body div container "这是容器"`

#### insert - 插入元素
```bash
insert insertLocation tagName idValue [textContent]
```
在指定元素之前插入一个新元素。
- `insertLocation`：目标位置元素的ID，新元素将插入到此元素之前
- `tagName`：新元素的HTML标签名
- `idValue`：新元素的ID属性值，必须是唯一的
- `textContent`：可选参数，指定新元素的文本内容

示例：`insert paragraph h2 heading "新标题"`

#### delete - 删除元素
```bash
delete elementId
```
删除指定ID的元素及其所有子元素。
- `elementId`：要删除的元素ID

示例：`delete sidebar`

#### edit-text - 编辑元素文本
```bash
edit-text elementId [newTextContent]
```
修改指定元素的文本内容。
- `elementId`：要编辑的元素ID
- `newTextContent`：新的文本内容，如果不提供则清空文本

示例：`edit-text paragraph "这是更新后的段落内容"`

#### edit-id - 修改元素ID
```bash
edit-id oldId newId
```
修改元素的ID属性。
- `oldId`：元素当前的ID
- `newId`：元素的新ID，必须是唯一的

示例：`edit-id old_button new_button`

### 查看命令

#### print-tree - 显示HTML结构
```bash
print-tree
```
以树状格式显示当前HTML文档的结构，便于查看文档的层次关系。如果有拼写错误的元素，会在元素前显示[X]标记。

#### showid - 控制ID显示
```bash
showid true
showid false
```
控制在树状显示中是否显示元素的ID属性。
- `true`：显示元素ID
- `false`：不显示元素ID

此设置针对当前活动的编辑文件有效。

#### dir-tree - 显示文件目录
```bash
dir-tree
```
显示当前工作目录的文件和子目录结构，类似于IDE中的资源管理器视图。当前打开编辑的文件会在名称后面显示星号(*)标记。

### 拼写检查

#### spell-check - 拼写检查
```bash
spell-check
```
检查当前HTML文档中所有文本内容的拼写错误，并显示错误报告。后续使用`print-tree`命令时，拼写错误的元素会被标记为[X]。

### 历史操作

#### undo - 撤销操作
```bash
undo
```
撤销上一步编辑操作。可以连续执行多次undo来撤销多步操作。注意，保存文件后将无法撤销之前的操作。

#### redo - 重做操作
```bash
redo
```
重新执行之前被撤销的操作。如果在撤销后执行了新的编辑操作，则无法使用redo重做之前撤销的操作。

### 会话管理

#### editor-list - 显示文件列表
```bash
editor-list
```
显示当前session中打开的所有文件列表。显示格式如下：
- 当前活动文件前面会显示">"符号
- 已修改但未保存的文件名后面会显示"*"符号

#### edit - 切换编辑文件
```bash
edit filename.html
```
切换到另一个已打开的文件进行编辑。指定的文件必须已经通过`load`命令加载。

#### exit - 退出程序
```bash
exit
```
保存当前会话状态并退出编辑器。会话状态包括打开的文件列表、当前活动文件以及每个文件的showid设置，下次启动编辑器时会自动恢复这些状态。

## 使用示例

### 创建简单文档

```
init
append body div container
append container h1 title "Hello World"
append container p intro "This is a paragraph"
save example.html
```

### 编辑多个文件

```
load example.html
load another.html
editor-list
edit example.html
append container ul list
save
```

### 目录和文件导航

```
dir-tree
edit another.html
showid false
print-tree
```

### 编辑文档

```
load example.html
append container ul list
append list li item1 "First item"
append list li item2 "Second item"
save
```

### 撤销操作

```
append container p footer "Footer text"
print-tree
undo
print-tree
redo
print-tree
```

## 会话恢复

退出程序时（使用`exit`命令），编辑器会自动保存当前会话状态。下次启动编辑器时，将自动恢复：

1. 上次打开的文件列表
2. 活动编辑的文件
3. 每个文件的showID设置

## 提示和技巧

1. 使用Tab键可以自动补全命令和文件名
2. 操作前先使用`print-tree`命令查看当前文档结构
3. 定期保存文件以防数据丢失
4. 使用`--help`选项查看命令详细用法

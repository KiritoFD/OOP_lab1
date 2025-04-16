# UML图表使用说明

## 查看PlantUML图的方法（无需JAR文件）

### 1. 在线PlantUML服务

1. 访问以下任一在线服务：
   - http://www.plantuml.com/plantuml/
   - https://plantuml-editor.kkeisuke.dev/
   - https://www.planttext.com/

2. 复制`class_diagram.puml`文件的内容粘贴到网站中
3. 图表将自动生成和显示

### 2. 使用VS Code扩展

1. 在VS Code中安装"PlantUML"扩展
2. 打开`.puml`文件
3. 使用以下方法之一查看图表：
   - 右键菜单选择"PlantUML: Preview Current Diagram"
   - 使用快捷键Alt+D
   - 点击编辑器右上角的预览图标

### 3. 使用其他IDE插件

- IntelliJ IDEA: "PlantUML integration"插件
- Eclipse: "PlantUML Eclipse Plugin"

### 4. 将图表导出为图片格式

可以使用在线服务将PlantUML导出为PNG、SVG、PDF等格式，以便在任何环境下查看。

## 图表说明

`class_diagram.puml`包含HTML编辑器项目的完整类结构，主要展示：

- 核心数据模型（HtmlElement, HtmlModel）
- 命令模式实现（Command及其子类）
- 会话管理（Editor, SessionManager）
- 应用层结构（Application, CommandParser）
- IO模块和工具类
- 各组件间的依赖关系

此图表准确反映了当前项目的架构设计，可以作为开发参考。

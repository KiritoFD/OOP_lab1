# 测试输入目录

此目录用于存放测试样例文件。请手动创建以下类型的测试样例：

1. HTML 文档样例
2. 编辑命令序列样例 
3. 预期结果样例

## 建议的测试样例格式

### HTML 样例文件
```html
<html>
  <body id="body">
    <div id="div1">示例内容</div>
  </body>
</html>
```

### 命令序列样例
可以使用 JSON 或其他格式记录命令序列，例如：
```json
[
  {
    "command": "insert",
    "tag": "p",
    "id": "p1",
    "location": "div1",
    "text": "插入的段落"
  },
  {
    "command": "append",
    "tag": "span",
    "id": "span1",
    "parent_id": "p1",
    "text": "追加的文本"
  }
]
```

请在此目录中手动创建测试样例文件，而不是通过代码生成它们。

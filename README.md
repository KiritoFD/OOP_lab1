# HTML编辑器项目
https://deepwiki.com/KiritoFD/OOP_lab1
<div align="center">
  <img src="docs/images/logo.png" alt="HTML编辑器" width="200" height="200">
  <br>
  <p>
    <strong>一款功能强大的HTML文档编辑工具</strong>
  </p>
  <p>
    <a href="#快速开始">快速开始</a> •
    <a href="#核心功能">核心功能</a> •
    <a href="#文档导航">文档</a> •
    <a href="#架构特点">架构</a> •
    <a href="#测试">测试</a>
  </p>
</div>

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/yourusername/html-editor.git
cd html-editor

# 安装依赖
pip install -r requirements.txt

# 启动编辑器
python run.py
```

## 核心功能

- 📝 **HTML编辑** - 创建、修改和删除HTML元素
- 💾 **文件操作** - 读写HTML文件，支持多文件会话
- 🔍 **树形可视化** - 直观展示文档结构
- ↩️ **撤销/重做** - 完整的操作历史控制
- 📊 **拼写检查** - 智能识别和修正拼写错误
- 🔄 **会话管理** - 支持多文件同时编辑

## 文档导航

| 文档                                                   | 说明                   |
| ------------------------------------------------------ | ---------------------- |
| [**📚 项目概述**](docs/PROJECT_OVERVIEW.md)         | 项目总体介绍与结构说明 |
| [**🏗️ 架构设计**](docs/architecture.md)           | 分层架构与模块说明     |
| [**📊 系统图表**](docs/complete_project_diagram.md) | 可视化系统架构与流程   |
| [**🔗 依赖关系**](docs/detailed_dependencies.md)    | 模块间依赖详解         |
| [**📖 用户指南**](docs/USER_GUIDE.md)               | 使用说明与命令示例     |
| [**📋 UML类图**](system_architecture.puml)          | 系统UML类图            |
| [**🧪 测试指南**](README_TESTING.md)                | 测试系统使用方法       |

## 架构特点

编辑器采用精心设计的分层架构：

```
应用层 → 会话层 → 命令层 → 核心层 → I/O层 → 工具层
                  ↓             ↓
               拼写检查层 ←─────┘
```

### 设计模式

系统融合多种设计模式，构建灵活可扩展的架构：

- **命令模式** - 封装所有编辑操作，支持撤销/重做
- **组合模式** - HTML元素树的优雅实现
- **访问者模式** - 无侵入式树遍历和处理
- **观察者模式** - 命令执行状态通知机制
- **适配器模式** - 无缝整合第三方库

更多架构细节请参阅[架构设计文档](docs/architecture.md)。

## 项目结构

```
src/               # 源代码目录
├── application/   # 应用层
├── commands/      # 命令层
├── core/          # 核心层
├── io/            # IO层
├── session/       # 会话层
├── spellcheck/    # 拼写检查层
└── utils/         # 工具层
tests/             # 测试目录
├── unit/          # 单元测试
├── integration/   # 集成测试
└── system/        # 系统测试
```

## 测试

```bash
# 运行所有测试
python -m pytest

# 运行单元测试
python -m pytest tests/unit/

# 运行集成测试
python -m pytest tests/integration/

# 运行特定测试
python -m pytest tests/unit/core/

# 使用交互式测试工具
python run_interactive_tests.py
```

详细测试指南请参阅[测试文档](README_TESTING.md)。

## 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件

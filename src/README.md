# Source Code

本目录包含 Refrain 项目的源代码。

## 目录结构

```
src/
└── refrain/          # Refrain 主包
    ├── cli/          # 命令行交互层
    ├── core/         # 基础配置层
    ├── engine/       # 核心调度层
    ├── skills/       # 工具技能层
    ├── utils/        # 通用工具层
    └── resources/    # 资源文件
```

## 说明

采用 **src layout** 结构的好处：
- 避免开发时意外导入源码目录
- 确保测试运行的是安装后的包
- 打包时自动排除非代码文件
- 符合 Python Packaging Authority 推荐标准

## 开发安装

```bash
pip install -e .
```

这会将 `src/refrain` 安装为可编辑模式，修改代码后立即生效。

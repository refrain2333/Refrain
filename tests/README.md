# Refrain 测试指南

## 运行测试

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_cli.py

# 运行特定测试
pytest tests/test_cli.py::test_version_command

# 显示详细输出
pytest -v

# 显示 print 输出
pytest -s

# 生成覆盖率报告
pytest --cov=refrain --cov-report=html
```

## 测试结构

```
tests/
├── __init__.py
├── conftest.py       # pytest 配置和 fixtures
├── test_cli.py       # CLI 命令测试
├── test_core.py      # Core 模块测试
└── test_utils.py     # Utils 工具测试
```

## 编写测试

每个测试文件应该：
1. 以 `test_` 开头
2. 测试函数也以 `test_` 开头
3. 使用 fixtures 来准备测试数据
4. 包含清晰的断言

示例：
```python
def test_something():
    result = function_to_test()
    assert result == expected_value
```

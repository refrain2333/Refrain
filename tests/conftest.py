"""
pytest 配置文件
定义测试 fixtures 和全局配置
"""
import pytest
from pathlib import Path


@pytest.fixture
def sample_python_file(tmp_path):
    """创建一个临时的 Python 文件用于测试"""
    file = tmp_path / "sample.py"
    file.write_text("""
def hello(name):
    print(f"Hello, {name}!")

if __name__ == "__main__":
    hello("World")
""")
    return file


@pytest.fixture
def project_root():
    """获取项目根目录"""
    return Path(__file__).parent.parent

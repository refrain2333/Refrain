"""
CLI 命令测试
"""
import pytest
from typer.testing import CliRunner
from refrain.cli import app

runner = CliRunner()


def test_version_command():
    """测试 version 命令"""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "Refrain" in result.stdout


def test_model_list_command():
    """测试 model list 命令"""
    result = runner.invoke(app, ["model", "list"])
    assert result.exit_code == 0
    # 应该包含模型列表
    assert "gpt" in result.stdout.lower() or "模型" in result.stdout


def test_edit_command_file_not_exist():
    """测试 edit 命令 - 文件不存在"""
    result = runner.invoke(app, ["edit", "nonexistent.py", "修改代码"])
    # 应该报错
    assert result.exit_code != 0

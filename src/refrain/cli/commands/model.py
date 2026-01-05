"""
模型管理子命令模块
提供模型列表、切换等功能
"""
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()


@app.command("list")
def list_models():
    """列出可用的 AI 模型"""
    # TODO: 从 core.config 读取模型配置
    
    table = Table(title="可用模型")
    table.add_column("名称", style="cyan")
    table.add_column("Provider", style="green")
    table.add_column("Model ID", style="magenta")
    table.add_column("状态", style="yellow")
    
    # 示例数据（后续从配置读取）
    table.add_row("gpt-4o", "OpenAI", "gpt-4o", "✅ 当前")
    table.add_row("gpt-3.5", "OpenAI", "gpt-3.5-turbo", "")
    table.add_row("deepseek", "DeepSeek", "deepseek-chat", "")
    
    console.print(table)


@app.command("use")
def use_model(name: str = typer.Argument(..., help="模型名称")):
    """切换当前使用的模型"""
    # TODO: 调用 core.config.set_current_model()
    
    console.print(f"[green]✔ 已切换到模型: {name}[/]")
    console.print(f"[dim]配置已保存到 ~/.refrain/config.json[/]")


@app.command("info")
def model_info():
    """显示当前模型信息"""
    # TODO: 读取当前模型配置
    
    console.print("[cyan]当前模型信息[/]")
    console.print("  名称: gpt-4o")
    console.print("  Provider: OpenAI")
    console.print("  API Key: sk-****...****")

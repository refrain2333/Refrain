"""
CLI 主入口 - 命令行应用定义与子命令注册中心
"""
import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# 导入子命令模块
from .commands import model, chat

app = typer.Typer(help="Refrain: Python AI Code Assistant")
console = Console()

# ========== 子命令注册中心 ==========
app.add_typer(model.app, name="model", help="模型管理")
app.add_typer(chat.app, name="chat", help="交互式聊天")
# app.add_typer(config.app, name="config", help="配置管理")  # 未来
# app.add_typer(project.app, name="project", help="项目分析")  # 未来


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    """
    Refrain: Python AI Code Assistant
    默认进入交互式聊天模式
    """
    if ctx.invoked_subcommand is None:
        from .commands.chat import ChatSession
        import asyncio
        session = ChatSession()
        asyncio.run(session.run())


@app.command()
def edit(
    file: Path = typer.Argument(..., exists=True, dir_okay=False, help="要编辑的文件"),
    instruction: str = typer.Argument(..., help="修改指令"),
):
    """编辑指定文件"""
    console.print(f"[bold blue]Refrain[/] 正在分析 {file.name}...")
    console.print(f"[dim]指令: {instruction}[/]")
    
    # TODO: 调用 orchestrator 进行实际处理
    # from ...engine.orchestrator import orchestrator
    # reasoning, new_code = orchestrator.process_task(file, instruction)
    
    console.print("[yellow]⚠ 功能开发中...[/]")


@app.command()
def version():
    """显示版本信息"""
    console.print("[bold cyan]Refrain v0.2.0[/]")
    console.print("[dim]Python AI Code Assistant[/]")


if __name__ == "__main__":
    app()

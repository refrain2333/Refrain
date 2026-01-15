"""
模型管理子命令模块
提供模型列表、切换、添加等功能
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from refrain.core.config import user_config, ModelProfile, interactive_add_model

app = typer.Typer(help="管理 AI 模型配置 (Profiles)")
console = Console()


@app.command("list")
def list_models():
    """列出所有已配置的模型预设"""
    table = Table(title="Refrain 模型预设列表")
    table.add_column("别名", style="cyan")
    table.add_column("供应商", style="green")
    table.add_column("模型 ID", style="magenta")
    table.add_column("认证方式", style="blue")
    table.add_column("状态", style="yellow")

    cfg = user_config.config
    for name, profile in cfg.profiles.items():
        auth_method = f"🔑 {profile.api_key_env}" if profile.api_key_env else "🔐 keyring"
        is_active = "✅ 当前使用" if name == cfg.current_model else ""
        table.add_row(name, profile.provider or "-", profile.model, auth_method, is_active)

    console.print(table)


@app.command("use")
def use_model(name: str = typer.Argument(..., help="模型别名")):
    """切换当前默认使用的模型"""
    if name not in user_config.config.profiles:
        console.print(f"[red]错误: 未找到模型 '{name}'[/]")
        available = ", ".join(user_config.config.profiles.keys())
        console.print(f"[dim]可用: {available}[/]")
        raise typer.Exit(code=1)

    user_config.current_model_name = name
    console.print(f"[green]✓ 已切换到: {name}[/]")


@app.command("info")
def model_info():
    """显示当前激活模型的详细信息"""
    try:
        profile = user_config.get_active_profile()
        console.print(f"[cyan]当前模型: {profile.name}[/]")
        console.print(f"  供应商: {profile.provider or '未指定'}")
        console.print(f"  模型 ID: {profile.model}")
        console.print(f"  LiteLLM ID: {profile.litellm_id}")
        console.print(f"  认证: {'环境变量 ' + profile.api_key_env if profile.api_key_env else 'keyring'}")
        console.print(f"  API: {profile.base_url or '默认'}")
        console.print(f"  Temperature: {profile.temperature}")
    except ValueError as e:
        console.print(f"[red]{e}[/]")


@app.command("add")
def add_model(
    name: str = typer.Option(..., "--name", "-n", help="模型别名"),
    provider: str = typer.Option("openai", "--provider", "-p", help="供应商"),
    model: str = typer.Option(..., "--model", "-m", help="模型 ID"),
    env_var: str = typer.Option("", "--env", "-e", help="环境变量名 (留空使用 keyring)"),
    base_url: str = typer.Option(None, "--url", "-u", help="API 地址"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="交互式添加"),
):
    """添加新模型配置"""
    if interactive or not any([name, provider, model]):
        new_profile = interactive_add_model()
        if not new_profile:
            raise typer.Exit()
    else:
        new_profile = ModelProfile(
            name=name,
            provider=provider,
            model=model,
            api_key_env=env_var,
            base_url=base_url,
        )

    user_config.config.profiles[new_profile.name] = new_profile
    user_config.save()
    console.print(f"[green]✓ 已添加模型: {new_profile.name}[/]")


@app.command("remove")
def remove_model(name: str = typer.Argument(..., help="要移除的模型别名")):
    """移除模型配置"""
    if name not in user_config.config.profiles:
        console.print(f"[red]错误: 模型 '{name}' 不存在[/]")
        raise typer.Exit(code=1)

    if len(user_config.config.profiles) <= 1:
        console.print("[red]错误: 无法删除最后一个模型预设。请先添加一个新预设。[/]")
        raise typer.Exit(code=1)

    del user_config.config.profiles[name]
    if user_config.current_model_name == name:
        new_default = next(iter(user_config.config.profiles))
        user_config.current_model_name = new_default
        console.print(f"[yellow]⚠️  当前模型已移除，已自动切换到: {new_default}[/]")
    
    user_config.save()
    console.print(f"[green]✓ 已移除模型: {name}[/]")

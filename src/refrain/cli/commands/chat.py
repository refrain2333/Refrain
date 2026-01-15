"""
交互式聊天子命令模块 - 极简克制风格 (Claude Code Inspired)
"""
import asyncio
import sys
import os
from pathlib import Path
import typer
from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from rich.align import Align
from rich.table import Table

from refrain.core.llm.chat.factory import get_llm_backend
from refrain.core.config import (
    user_config, settings, interactive_add_model_async, 
    get_api_key_from_keyring
)
from refrain.core.logger import log

app = typer.Typer(help="与 AI 助手直接对话")
console = Console()

def get_minimal_logo():
    """极简风格的像素 Logo"""
    logo = Text.assemble(
        (" ▟▀▖ ", "cyan"), ("Refrain ", "bold white"), ("AI Assistant ", "dim"), 
        (f"v0.2.0", "dim italic")
    )
    return logo

class ChatSession:
    def __init__(self):
        self.messages = []
        self.llm = None
        self._load_system_prompt()
        
    def _load_system_prompt(self):
        try:
            system_path = Path(settings.PROJECT_ROOT) / "src" / "refrain" / "resources" / "system.md"
            if system_path.exists():
                content = system_path.read_text(encoding="utf-8")
                self.messages.append({"role": "system", "content": content})
            else:
                self.messages.append({"role": "system", "content": "You are Refrain, a helpful AI code assistant."})
        except Exception:
            self.messages.append({"role": "system", "content": "You are Refrain, a helpful AI code assistant."})

    def _has_valid_auth(self, profile) -> bool:
        # 如果 api_key_env 看起来像个 Key（以 sk- 开头），判定为配置错误
        if profile.api_key_env.startswith("sk-"):
            return False
        if profile.api_key_env:
            return bool(os.getenv(profile.api_key_env))
        return bool(get_api_key_from_keyring(profile.name))

    def _get_status_line(self):
        """生成极简的状态行"""
        try:
            profile = user_config.get_active_profile()
            is_ready = self._has_valid_auth(profile)
            status_color = "green" if is_ready else "red"
            status_text = "Ready" if is_ready else "Key Missing"
            
            return Text.assemble(
                ("● ", status_color),
                (f"{profile.name} ", "bold white"),
                (f"({profile.model}) ", "dim"),
                ("· ", "dim"),
                (status_text, "dim")
            )
        except Exception:
            return Text("● No model configured", style="red")

    async def _check_and_init_llm(self) -> bool:
        try:
            profile = user_config.get_active_profile()
            
            # 特殊校验：防止用户把 Key 填成了环境变量名
            if profile.api_key_env.startswith("sk-"):
                console.print(Panel(
                    Group(
                        Text("检测到配置错误！", style="bold red"),
                        Text("\n你似乎把 [bold red]API Key[/] 填到了 [bold cyan]环境变量名[/] 这一项中。"),
                        Text("\n请在聊天框输入 [bold yellow]/config[/] 重新配置，选择 '现在输入 API Key'。"),
                    ),
                    border_style="red", padding=(1, 1)
                ))
                return False

            if not self._has_valid_auth(profile):
                console.print(Panel(
                    Group(
                        Text(f"模型 {profile.name} 尚未认证", style="yellow"),
                        Text(f"\n运行: [bold green]export {profile.api_key_env}=your_key[/]"),
                        Text("\n或者输入 [bold yellow]/config[/] 使用交互式配置。"),
                    ),
                    border_style="yellow", padding=(1, 1)
                ))
                return False
            
            self.llm = get_llm_backend()
            return True
        except Exception as e:
            console.print(f"[red]初始化失败: {e}[/]")
            return False

    async def run(self):
        # 1. 打印极简 Logo
        console.print(get_minimal_logo())
        # 2. 打印状态行
        console.print(self._get_status_line())
        console.print()
        
        await self._check_and_init_llm()
        
        while True:
            try:
                # 极简 Prompt
                user_input = console.input("[bold cyan]❯ [/]").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ["/exit", "exit", "quit", ":q"]:
                    console.print("[dim]Goodbye.[/]")
                    break
                    
                if user_input.lower() == "/clear":
                    self.messages = [self.messages[0]] if self.messages else []
                    console.print("[dim]Context cleared.[/]")
                    continue

                if user_input.lower() == "/config":
                    new_p = await interactive_add_model_async()
                    if new_p:
                        user_config.config.profiles[new_p.name] = new_p
                        user_config.current_model_name = new_p.name
                        self.llm = None
                        console.print("[dim]Profile updated.[/]")
                    continue

                if not self.llm:
                    if not await self._check_and_init_llm(): continue

                self.messages.append({"role": "user", "content": user_input})
                await self._process_response()
                
            except KeyboardInterrupt:
                console.print("\n[dim]Use /exit to quit.[/]")
                continue
            except EOFError:
                break

    async def _process_response(self):
        full_content = ""
        full_reasoning = ""
        
        # 使用更低调的 Live 状态
        with Live(Text("Thinking...", style="dim italic"), console=console, transient=True) as live:
            try:
                async for chunk in self.llm.stream_chat(self.messages):
                    if chunk.reasoning_content:
                        full_reasoning += chunk.reasoning_content
                    if chunk.content:
                        full_content += chunk.content
                    
                    elements = []
                    if full_reasoning:
                        elements.append(Panel(
                            Text(full_reasoning, style="dim italic"),
                            title="Thinking", title_align="left",
                            border_style="dim", padding=(0, 1)
                        ))
                    
                    if full_content:
                        elements.append(Markdown(full_content))
                    
                    if elements:
                        live.update(Group(*elements))
                
                self.messages.append({"role": "assistant", "content": full_content})
                    
            except Exception as e:
                console.print(f"\n[bold red]Error:[/] {e}")
                log.error(f"Chat Error: {e}")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Refrain Interactive Chat"""
    if ctx.invoked_subcommand is None:
        session = ChatSession()
        asyncio.run(session.run())

if __name__ == "__main__":
    app()

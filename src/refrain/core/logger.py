import sys
from pathlib import Path
from loguru import logger as _logger
from refrain.core.config import settings

# 基础日志目录
# 延迟计算，确保 settings 已完全加载
def get_log_dir():
    log_dir = Path(settings.PROJECT_ROOT) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir

def setup_logger():
    """
    基础配置：仅配置终端输出。
    设置为 ERROR 级别，确保 CLI 界面干净，不被日常日志干扰。
    """
    _logger.remove()

    # 终端仅显示严重错误
    _logger.add(
        sys.stderr,
        format="<red><b>{level}</b></red> | {message}",
        level="ERROR",
        colorize=True,
        # 排除掉专门的 chat_trace 日志，防止其进入终端
        filter=lambda r: "is_chat" not in r["extra"]
    )
    return _logger

def init_file_logging():
    """
    文件日志初始化：
    1. 开启 runtime.log 供另一个终端进行 tail -f 实时观察。
    2. 开启 chat trace 用于对话复盘。
    """
    base_log_dir = get_log_dir()
    
    # 1. 详细运行日志 (固定文件名，由 loguru 处理滚动)
    runtime_path = base_log_dir / "runtime.log"
    _logger.add(
        str(runtime_path),
        format="{time:HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG" if settings.DEBUG else "INFO",
        rotation="10 MB",
        retention="1 week",
        encoding="utf-8",
        enqueue=True,
        filter=lambda r: "is_chat" not in r["extra"]
    )

    # 2. 对话追踪 (按天滚动，方便复盘)
    trace_path = base_log_dir / "trace" / "trace_{time:YYYY-MM-DD}.jsonl"
    _logger.add(
        str(trace_path),
        format="{message}", 
        level="INFO",
        filter=lambda r: "is_chat" in r["extra"],
        rotation="00:00",
        retention="90 days",
        encoding="utf-8",
        enqueue=True
    )
    _logger.info("日志系统已全面激活 (双窗口模式已就绪)")

# 初始化全局 log 对象
log = setup_logger()

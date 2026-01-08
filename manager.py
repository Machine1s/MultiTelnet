import click
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.live import Live
from rich.columns import Columns

from core.inventory import InventoryManager
from core.executor import RemoteExecutor, ExecutionResult
from core.analyzer import ResultAnalyzer, SimpleLogger, HealthParser

console = Console()

@click.group()
def cli():
    """MultiTelnet - 40台远程主机批量管理工具"""
    pass

@cli.command()
@click.option('--group', default='all', help='指定要操作的主机组')
@click.option('--cmd', required=True, help='要执行的命令')
@click.option('--workers', default=40, help='并发线程数')
@click.option('--show-ip', is_flag=True, help='显示原始 IP 和端口而非别名')
def exec(group, cmd, workers, show_ip):
    """批量执行命令并展示结果对比"""
    
    # --- 增加敏感词防火墙逻辑 ---
    DANGEROUS_COMMANDS = ["rm ", "reboot", "shutdown", "init 0", "init 6", "mkfs", "dd if="]
    is_dangerous = any(bad in cmd.lower() for bad in DANGEROUS_COMMANDS)
    
    if is_dangerous:
        console.print(Panel(
            f"[bold white on red] !!! 安全警告 !!! [/bold white on red]\n\n"
            f"检测到敏感指令: [yellow]{cmd}[/yellow]\n"
            f"该命令可能导致服务器宕机或数据丢失，已被防火墙拦截。\n"
            f"如果确需执行，请通过本地终端手动单独操作。",
            title="Security Shield",
            border_style="red"
        ))
        return
    # ---------------------------
    
    # 1. 加载配置
    inventory_path = os.path.join(os.getcwd(), 'inventory', 'hosts.yaml')
    if not os.path.exists(inventory_path):
        console.print(f"[bold red]错误:[/bold red] 找不到配置文件 {inventory_path}")
        return

    mgr = InventoryManager(inventory_path)
    hosts = mgr.get_hosts(group)
    
    if not hosts:
        console.print(f"[yellow]提示:[/yellow] 在组 '{group}' 中未找到任何主机。")
        return

    console.print(Panel(f"正在对 [bold cyan]{len(hosts)}[/bold cyan] 台主机执行命令: [green]{cmd}[/green]"))

    # 2. 执行引擎
    executor = RemoteExecutor(max_workers=workers)
    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]正在分发指令...", total=len(hosts))
        
        def update_progress(res):
            progress.advance(task)
        
        results = executor.run_batch(hosts, cmd, progress_callback=update_progress)

    # 3. 日志记录
    logger = SimpleLogger(os.path.join(os.getcwd(), 'logs'))
    logger.log_results(results)

    # 4. 生成结果表格
    table = Table(title="执行结果汇总", show_header=True, header_style="bold magenta")
    table.add_column("Host", style="dim")
    table.add_column("Status")
    table.add_column("Duration", justify="right")
    table.add_column("Output Preview", ratio=1)

    for r in results:
        status_str = f"[green]✔ SUCCESS[/green]" if r.status == 'SUCCESS' else f"[red]✘ {r.error}[/red]"
        output_preview = r.output[:50] + "..." if len(r.output) > 50 else r.output
        display_name = f"{r.host}:{r.port}" if show_ip else r.alias
        table.add_row(display_name, status_str, f"{r.duration}s", output_preview)

    console.print(table)

    # 5. 异构分析 (特色功能)
    analysis = ResultAnalyzer.group_by_output(results)
    if len(analysis) > 1:
        console.print(Panel("[bold yellow]检测到输出不一致！[/bold yellow] 结果已并归类如下：", border_style="yellow"))
        for out, host_list in analysis.items():
            hosts_str = ", ".join(host_list)
            display_out = out if len(out) < 30 else out[:27] + "..."
            console.print(f"[bold white]输出: '{display_out}'[/bold white]")
            console.print(f"  └─ 主机: {hosts_str}")
    else:
        console.print("[bold green]所有主机输出完全一致。[/bold green]")

@cli.command()
@click.option('--group', default='all', help='指定要检查的主机组')
@click.option('--workers', default=40, help='并发线程数')
def health(group, workers):
    """一键系统健康体检表 (Load, Mem, Disk)"""
    
    inventory_path = os.path.join(os.getcwd(), 'inventory', 'hosts.yaml')
    mgr = InventoryManager(inventory_path)
    hosts = mgr.get_hosts(group)
    
    if not hosts:
        console.print(f"[yellow]提示:[/yellow] 在组 '{group}' 中未找到任何主机。")
        return

    # 定义体检指令集
    health_cmds = {
        "Load": "uptime",
        "Memory": "free -m",
        "Disk": "df -h /"
    }
    
    all_results = {}
    executor = RemoteExecutor(max_workers=workers)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        overall_task = progress.add_task("[cyan]正在进行系统体检...", total=len(health_cmds) * len(hosts))
        
        for name, cmd in health_cmds.items():
            def cb(res): progress.advance(overall_task)
            all_results[name] = executor.run_batch(hosts, cmd, progress_callback=cb)

    # 解析数据
    metrics = HealthParser.parse_metrics(all_results)
    
    # 渲染结果表格
    table = Table(title="服务器健康状态仪表盘", header_style="bold cyan", border_style="dim")
    table.add_column("主机别名", style="white")
    table.add_column("状态")
    table.add_column("负载 (1min)", justify="center")
    table.add_column("内存使用率", justify="center")
    table.add_column("磁盘占用 (/)", justify="center")

    for alias, data in metrics.items():
        status = "[green]ONLINE[/green]" if data["status"] == "ONLINE" else "[red]OFFLINE[/red]"
        
        # 负载颜色逻辑
        load_val = data["load"]
        load_display = str(load_val)
        if isinstance(load_val, float):
            if load_val > 5.0: load_display = f"[red]{load_val}[/red]"
            elif load_val > 2.0: load_display = f"[yellow]{load_val}[/yellow]"
            else: load_display = f"[green]{load_val}[/green]"
            
        # 内存/磁盘颜色逻辑 (百分比)
        def color_pct(val):
            if not isinstance(val, int): return "-"
            if val > 90: return f"[bold red]{val}%[/bold red]"
            if val > 70: return f"[yellow]{val}%[/yellow]"
            return f"[green]{val}%[/green]"

        table.add_row(
            alias, 
            status, 
            load_display, 
            color_pct(data["mem"]), 
            color_pct(data["disk"])
        )

    console.print(table)
    console.print("\n[dim]注: 负载 > 2.0 或 资源占用 > 70% 将会被标记为预警状态。[/dim]")

if __name__ == "__main__":
    cli()
#hello
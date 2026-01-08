import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
from typing import List, Dict

@dataclass
class ExecutionResult:
    host: str
    port: int
    group: str
    alias: str
    command: str
    status: str  # 'SUCCESS' or 'FAILED'
    output: str
    error: str
    start_time: str
    duration: float

class RemoteExecutor:
    def __init__(self, max_workers: int = 40):
        self.max_workers = max_workers

    def _execute_single(self, host_cfg, command: str) -> ExecutionResult:
        start_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_ts = time.time()
        
        device = {
            'device_type': 'linux' if host_cfg.protocol == 'ssh' else 'generic_telnet',
            'host': host_cfg.hostname,
            'username': host_cfg.username,
            'password': host_cfg.password,
            'port': host_cfg.port,
            'conn_timeout': 30,          # 强力模式：连接超时增加到30秒
            'global_delay_factor': 3,    # 强力模式：全局延迟系数增加到3
            'fast_cli': False,           # 强力模式：禁用快显，确保稳定
        }

        output = ""
        error = ""
        status = "SUCCESS"

        try:
            # 建立连接
            with ConnectHandler(**device) as conn:
                # 模糊匹配提示符，解决现场极其不标准的 Shell Prompt 问题
                output = conn.send_command(command, expect_string=r'[#\$>]')
        except NetmikoTimeoutException:
            status = "FAILED"
            error = "Connection Timeout"
        except NetmikoAuthenticationException:
            status = "FAILED"
            error = "Authentication Failed"
        except Exception as e:
            status = "FAILED"
            error = str(e)

        duration = round(time.time() - start_ts, 2)
        
        return ExecutionResult(
            host=host_cfg.hostname,
            port=host_cfg.port,
            group=host_cfg.group_name,
            alias=host_cfg.alias,
            command=command,
            status=status,
            output=output.strip(),
            error=error,
            start_time=start_time_str,
            duration=duration
        )

    def run_batch(self, hosts, command: str, progress_callback=None) -> List[ExecutionResult]:
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_host = {executor.submit(self._execute_single, h, command): h for h in hosts}
            for future in as_completed(future_to_host):
                res = future.result()
                results.append(res)
                if progress_callback:
                    progress_callback(res)
        return results

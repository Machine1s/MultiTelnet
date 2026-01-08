from collections import defaultdict
from typing import List, Dict
from core.executor import ExecutionResult
import json
import csv
import os
from datetime import datetime

class ResultAnalyzer:
    @staticmethod
    def group_by_output(results: List[ExecutionResult]) -> Dict[str, List[str]]:
        groups = defaultdict(list)
        for r in results:
            if r.status == 'SUCCESS':
                groups[r.output].append(r.alias)
            else:
                groups[f"[FAILED] {r.error}"].append(r.alias)
        return dict(groups)

class SimpleLogger:
    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        self.latest_log = os.path.join(log_dir, "latest_execution.csv")

    def log_results(self, results: List[ExecutionResult]):
        fieldnames = ['timestamp', 'alias', 'host', 'port', 'group', 'command', 'status', 'duration', 'output_summary', 'error']
        
        # 写入最新记录
        with open(self.latest_log, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow({
                    'timestamp': r.start_time,
                    'alias': r.alias,
                    'host': r.host,
                    'port': r.port,
                    'group': r.group,
                    'command': r.command,
                    'status': r.status,
                    'duration': r.duration,
                    'output_summary': r.output[:100].replace('\n', ' ') if r.output else "",
                    'error': r.error
                })
        
        # 同时追加到审计总日志
        audit_file = os.path.join(self.log_dir, "audit_history.csv")
        file_exists = os.path.isfile(audit_file)
        with open(audit_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for r in results:
                writer.writerow({
                    'timestamp': r.start_time,
                    'alias': r.alias,
                    'host': r.host,
                    'port': r.port,
                    'group': r.group,
                    'command': r.command,
                    'status': r.status,
                    'duration': r.duration,
                    'output_summary': r.output[:500].replace('\n', ' ') if r.output else "",
                    'error': r.error
                })

class HealthParser:
    """系统健康指标解析器"""
    @staticmethod
    def parse_metrics(results_map: Dict[str, List[ExecutionResult]]) -> Dict[str, dict]:
        """
        根据执行结果解析核心指标
        """
        metrics = {}
        # 结果是以命令为 Key 的映射
        # 我们需要按主机 Alias 进行聚合
        
        all_hosts = set()
        for res_list in results_map.values():
            for r in res_list:
                all_hosts.add(r.alias)
                
        for alias in all_hosts:
            metrics[alias] = {"status": "ONLINE", "load": "-", "mem": "-", "disk": "-"}

        for cmd, res_list in results_map.items():
            cmd = cmd.lower()
            for res in res_list:
                if res.status != "SUCCESS":
                    metrics[res.alias]["status"] = "OFFLINE"
                    continue
                
                output = res.output.lower()
                
                # 1. 解析负载 (uptime)
                if "load average" in output:
                    try:
                        load_part = output.split("load average:")[1].split(",")[0].strip()
                        metrics[res.alias]["load"] = float(load_part)
                    except: pass
                
                # 2. 解析内存 (free -m)
                if "mem:" in output:
                    try:
                        lines = output.splitlines()
                        for line in lines:
                            if "mem:" in line:
                                parts = line.split()
                                total = int(parts[1])
                                used = int(parts[2])
                                metrics[res.alias]["mem"] = int((used / total) * 100)
                    except: pass

                # 3. 解析磁盘 (df -h)
                if "/" in output and "%" in output:
                    try:
                        lines = output.splitlines()
                        for line in lines:
                            # 匹配根路径输出
                            if line.strip().endswith("/"):
                                parts = line.split()
                                for p in parts:
                                    if "%" in p:
                                        metrics[res.alias]["disk"] = int(p.replace("%", ""))
                    except: pass
        return metrics

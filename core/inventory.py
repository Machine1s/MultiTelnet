import yaml
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class HostConfig:
    hostname: str
    port: int
    username: str
    password: str
    protocol: str
    group_name: str
    alias: str

class InventoryManager:
    def __init__(self, yaml_path: str):
        self.yaml_path = yaml_path
        self.hosts: List[HostConfig] = []
        self._load()

    def _load(self):
        with open(self.yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        for group in data.get('inventory', []):
            group_name = group.get('name')
            protocol = group.get('protocol', 'ssh')
            username = group.get('username')
            password = group.get('password')
            default_port = 22 if protocol == 'ssh' else 23
            group_port = group.get('ports', default_port)
            
            for entry in group.get('hosts', []):
                alias = None
                if isinstance(entry, dict):
                    ip = entry.get('ip')
                    port = entry.get('port', group_port)
                    alias = entry.get('alias')
                else:
                    # 支持 127.0.0.1:2222 这种格式
                    if ':' in str(entry):
                        host_part, port_part = str(entry).split(':')
                        ip = host_part
                        port = int(port_part)
                    else:
                        ip = entry
                        port = group_port
                
                if not alias:
                    alias = f"{ip}:{port}"

                self.hosts.append(HostConfig(
                    hostname=ip,
                    port=port,
                    username=username,
                    password=password,
                    protocol=protocol,
                    group_name=group_name,
                    alias=alias
                ))

    def get_hosts(self, group_filter: Optional[str] = None) -> List[HostConfig]:
        if not group_filter or group_filter == 'all':
            return self.hosts
        return [h for h in self.hosts if h.group_name == group_filter]

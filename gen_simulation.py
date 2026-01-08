import os

def generate_simulation(count=10):
    # 1. 生成 docker-compose.yml
    dc_content = ["version: '3'\nservices:"]
    for i in range(1, count + 1):
        name = f"linux-node-{i:02d}"
        ssh_port = 2200 + i
        telnet_port = 2300 + i
        # 模拟现场的复杂主机名
        custom_hostname = f"ZS_S6_SITE_{i:02d}"
        
        dc_content.append(f"  {name}:")
        dc_content.append(f"    build: .")
        dc_content.append(f"    container_name: {name}")
        dc_content.append(f"    environment:")
        dc_content.append(f"      - HOSTNAME_CUSTOM={custom_hostname}")
        dc_content.append(f"    ports:")
        dc_content.append(f"      - \"{ssh_port}:22\"")
        dc_content.append(f"      - \"{telnet_port}:23\"")
        dc_content.append(f"    restart: always")

    with open('simulation/docker-compose.yml', 'w') as f:
        f.write("\n".join(dc_content))
    
    # 2. 生成对应的 inventory/hosts.yaml
    inv_content = ["inventory:"]
    
    # 前5个 SSH
    inv_content.append("  - name: ssh_group")
    inv_content.append("    protocol: ssh")
    inv_content.append("    username: root")
    inv_content.append("    password: admin123")
    inv_content.append("    hosts:")
    for i in range(1, 6):
        inv_content.append(f"      - ip: 127.0.0.1\n        port: {2200 + i}\n        alias: Node-{i:02d}-SSH")
        
    # 后5个 Telnet
    inv_content.append("  - name: telnet_group")
    inv_content.append("    protocol: telnet")
    inv_content.append("    username: root")
    inv_content.append("    password: admin123")
    inv_content.append("    hosts:")
    for i in range(6, 11):
        inv_content.append(f"      - ip: 127.0.0.1\n        port: {2300 + i}\n        alias: Node-{i:02d}-Telnet")

    with open('inventory/hosts.yaml', 'w') as f:
        f.write("\n".join(inv_content))

    print(f"成功生成 {count} 台主机的模拟配置（带自定义主机名模拟真实环境）。")
    print(f"- Docker Compose: simulation/docker-compose.yml")
    print(f"- Inventory: inventory/hosts.yaml")

if __name__ == "__main__":
    generate_simulation(40)

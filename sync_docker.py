import os

def sync_docker():
    # 抽取 Node-21 到 Node-40 的配置
    count_start = 21
    count_end = 40
    
    dc_content = ["version: '3'\nservices:"]
    for i in range(count_start, count_end + 1):
        name = f"linux-node-{i:02d}"
        ssh_port = 2200 + i
        telnet_port = 2300 + i
        dc_content.append(f"  {name}:")
        dc_content.append(f"    build: .")
        dc_content.append(f"    container_name: {name}")
        dc_content.append(f"    ports:")
        dc_content.append(f"      - \"{ssh_port}:22\"")
        dc_content.append(f"      - \"{telnet_port}:23\"")
        dc_content.append(f"    restart: always")

    with open('simulation/docker-compose.yml', 'w') as f:
        f.write("\n".join(dc_content))
    
    print(f"Docker Compose 已更新，仅保留 Node-{count_start} 到 Node-{count_end} (Telnet 组)。")

if __name__ == "__main__":
    sync_docker()

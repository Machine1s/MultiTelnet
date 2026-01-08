# MultiTelnet 使用手册 (User Guide)

MultiTelnet 是一款专为批量管理 Linux 主机设计的轻量级命令行工具。它支持 SSH 和 Telnet 双协议，具备并发执行、结果异构对比（寻找配置不同的机器）以及轻量级审计日志等核心功能。

---

## 1. 快速入门

### 1.1 软件部署
MultiTelnet 提供绿色版 `.exe` 文件，无需安装 Python 环境。
请确保文件夹包含以下结构：
```text
multiTelnet/
├── multiTelnet.exe        # 程序主体
├── inventory/             # 存放主机列表
│   └── hosts.yaml         # 主机配置文件（需手动编辑）
└── logs/                  # 自动生成的审计日志文件夹
```

### 1.2 配置主机 (inventory/hosts.yaml)
打开 `inventory/hosts.yaml`，按以下格式配置您的服务器。为了简化，您可以按“凭据组”进行配置：

```yaml
inventory:
  - name: web_cluster         # 组名，用于批量操作
    protocol: ssh             # 协议 (ssh 或 telnet)
    username: root
    password: "your_password"
    hosts:
      - ip: 192.168.1.10
        alias: Web-Server-01  # 自定义别名，提高可读性
      - ip: 192.168.1.11
        alias: Web-Server-02

  - name: legacy_switches
    protocol: telnet
    username: admin
    password: "admin_password"
    ports: 23
    hosts:
      - 10.0.0.5              # 简写模式：仅填写IP
```

---

## 2. 常用操作指令

在存放 `multiTelnet.exe` 的目录下打开命令提示符 (CMD) 或 PowerShell。

### 2.1 批量执行命令
对**所有**主机执行指令：
```bash
multiTelnet.exe exec --cmd "uname -a"
```

### 2.2 按组执行
仅对 `ssh_group` 组中的主机执行指令：
```bash
multiTelnet.exe exec --group ssh_group --cmd "uptime"
```

### 2.3 查看原始 IP 信息
默认展示自定义别名（Alias），如需查看原始 IP 和端口：
```bash
multiTelnet.exe exec --cmd "free -m" --show-ip
```

### 2.4 调整并发数
默认并发线程数为 40。如果网络环境较差，可以调低并发：
```bash
multiTelnet.exe exec --cmd "ls" --workers 10
```

---

## 3. 核心特色功能

### 3.1 异构分析 (Outlier Detection)
当命令执行完成后，如果不同主机的输出结果不一致，工具会自动进行归类。
*   **应用场景**：检查 40 台服务器的内核版本是否统一。如果其中 1 台版本不同，工具会将其高亮列出，无需人工逐行对比。

### 3.2 轻量级审计日志
每次执行的结果都会实时记录在 `logs/` 目录下：
*   **latest_execution.csv**：存放最近一次执行的详细结果。
*   **audit_history.csv**：追加记录所有历史操作，包含时间、主机名、命令、状态、耗时以及输出摘要。

---

## 4. 常见问题 (FAQ)

**Q: 为什么 SSH 连接比 Telnet 慢？**
A: SSH 协议由于存在复杂的加密握手和密钥协商过程，首次连接通常需要几秒钟。Telnet 是明文协议，几乎是瞬间连接。

**Q: 目标电脑拒绝连接 (Connection Refused)？**
A: 请检查：
1. 目标主机 IP 和端口是否正确。
2. 目标主机的 SSH 或 Telnet 服务是否安装并启动。
3. 防火墙是否放行了相应端口。

**Q: 如何开启命令行 Tab 补全？**
A: 在 PowerShell 中临时开启：
```powershell
$env:_MULTITELNET_COMPLETE = "ps_source"
./multiTelnet.exe | Out-String | Invoke-Expression
```

---
**版本**: v1.0.0  
**技术支持**: Powered by Antigravity AI

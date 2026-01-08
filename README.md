# MultiTelnet 🚀

**MultiTelnet** 是一个基于 Python 开发的专业级 Linux 服务器批量管理工具。它专为管理数十台（~40台）混合协议服务器（SSH/Telnet）而设计，提供了极速并发执行、健康状态仪表盘以及严苛的安全防火墙功能。

---

## ✨ 核心特性

- **🛡️ 安全卫士 (Security Guard)**：内置敏感指令拦截系统，防止误操作 `rm -rf`, `reboot`, `shutdown` 等危险命令。
- **📊 健康仪表盘 (Health Dashboard)**：一键巡检所有主机的负载 (Load)、内存 (Memory) 和磁盘 (Disk) 状态，并自动进行颜色预警。
- **⚡ 极速并发**：基于多线程池实现，支持同时对 40+ 台主机下发指令，无需排队。
- **🤝 双协议支持**：无缝支持 SSH 和老旧设备的 Telnet 协议，并针对弱网/复杂提示符环境进行了深度调优。
- **🔍 差异分析**：自动汇总执行结果，并智能识别哪些主机的输出与其他主机不一致。
- **📂 自动化审计**：所有执行记录自动保存为 `latest_execution.csv` 和带有时间戳的历史审计文件。

---

## 🛠️ 快速开始

### 1. 环境准备
建议使用 Python 3.8+ 环境：
```bash
pip install -r requirements.txt
```

### 2. 配置主机名册
编辑 `inventory/hosts.yaml`（可参考 `hosts.yaml.example`）：
```yaml
inventory:
  - name: my_servers
    protocol: ssh
    username: root
    password: your_password
    hosts:
      - 192.168.1.10
      - 192.168.1.11
```

---

## 🚀 常用指令

### 批量执行命令
```bash
python manager.py exec --group all --cmd "uptime"
```

### 一键系统体检
```bash
python manager.py health
```

### 构建独立可执行文件 (.exe)
```bash
python build_exe.py
```

---

## 📂 项目结构

```text
multiTelnet/
├── core/               # 核心引擎 (Executor, Inventory, Analyzer)
├── inventory/          # 配置文件目录
├── logs/               # 自动生成的流水记录
├── simulation/         # 基于 Docker 的本地模拟测试环境
├── manager.py          # CLI 入口程序
├── build_exe.py        # PyInstaller 打包脚本
└── requirements.txt    # 依赖项清单
```

---

## 🛡️ 安全提示

本工具包含强大的批量操作能力，请在执行涉及文件修改的操作前，务必在 `simulation` 模拟环境中进行测试。

---

## 👨‍💻 开发者学习记录
本项目包含完整的学习进阶路线，详见 [LEARNING_PLAN.md](./LEARNING_PLAN.md)。

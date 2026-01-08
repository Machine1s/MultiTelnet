# 多主机远程管理工具 (multiTelnet) 需求方案书

## 1. 项目背景
本项目旨在开发一个基于 Python 的核心管理工具，用于高效、批量地管理约 40 台 Linux 服务器。该工具需具备良好的扩展性、稳定的并发能力以及直观的操作界面。

## 2. 核心功能需求
- **多协议支持**：同时支持 SSH 和 Telnet 协议，并对上层调用隐藏协议差异。
- **并发执行**：支持对多台主机并发下发命令，提高操作效率。（需求：首先是为了查看一些数据，比如说内核版本，我希望可以快速对比出输出不同的那个主机。因为我管理的linux主机的一些相关配置都是相同的，所以我希望可以快速对比出输出不同的那个主机。这个可以作为一个小功能）
- **主机管理 (Inventory)**：通过配置文件管理主机列表，支持分组。
- **结果汇总**：清晰展示每台主机的执行结果（成功/失败、输出内容、耗时）。
- **健壮性**：具备超时处理、异常捕获及自动分级日志记录。（需求：要求可以轻量化的记录日志，日志内容要清晰，要包含主机名、命令、执行时间、执行结果、耗时等信息。）

## 3. 架构设计

### 3.1 逻辑分层
1.  **用户接口层 (CLI)**：基于 `click` 或 `argparse` 构建命令行交互。
2.  **调度层 (Runner)**：负责读取配置、初始化线程池并分发任务。
3.  **协议抽象层 (Abstraction)**：
    - 定义 `BaseConnection` 接口。
    - 实现 `SSHProvider` (基于 Paramiko/Netmiko)。
    - 实现 `TelnetProvider` (基于 telnetlib/Netmiko)。
4.  **展示层 (UI)**：利用 `Rich` 库实现表格化结果输出和进度条显示。

### 3.2 关键技术选型
- **语言**: Python 3.x
- **底层通信**: `Netmiko` (推荐，天然兼容 SSH 与 Telnet 且处理了繁琐的交互逻辑)
- **并发模型**: `ThreadPoolExecutor` (适合 40 台规模的 I/O 密集型任务)
- **配置格式**: `YAML` (易读易写)

## 4. 配置文件设计 (inventory/hosts.yaml)
为了简化配置，我们将主机按“凭据组”进行分类。每一组定义一套通用的用户名、密码和协议，下方直接列出所有适用该凭据的 IP 地址。

```yaml
# 这种结构允许你为不同类型的机器定义统一的登录信息
inventory:
  - name: internal_servers  # 组名，方便批量操作
    protocol: ssh
    username: admin
    password: "secure_password"
    hosts:
      - 192.168.1.10
      - 192.168.1.11
      - 192.168.1.12
      # ... 更多主机

  - name: legacy_devices
    protocol: telnet
    username: operator
    password: "old_password"
    ports: 23              # 可选，默认为协议标准端口
    hosts:
      - 10.0.0.5
      - 10.0.0.6
```

## 5. 预期操作界面 (CLI示例)
- **执行命令**: `python manager.py exec --group web_servers "df -h"`
- **查看状态**: `python manager.py status`

---
**请在此文档中直接修改您的想法，例如：**
- *是否需要支持文件批量上传/下载 (SFTP/SCP)？*
- *是否需要支持交互式 Shell 代理？*
- *对认证方式（密码 vs 密钥）的具体要求？*

# Agent 构建指南（源码保护）

## 目标

用 PyInstaller 将整个 Agent 打包为二进制，AMI 中不暴露 `.py` 源码。

## 前提条件

- 已有 conda 环境 `biomni_e1`（包含所有 Agent 依赖）
- 必须在与 AMI 相同的平台上打包（Ubuntu 22.04 x86_64）
- 建议直接在 EC2 Golden Instance 上操作

## 步骤

### 1. 安装 PyInstaller

```bash
conda activate biomni_e1
pip install pyinstaller
```

### 2. 打包

```bash
cd /path/to/agent

pyinstaller --onedir \
  --name biomni-agent \
  --hidden-import=biomni \
  --hidden-import=biomni.agent \
  --hidden-import=biomni.agent.a1 \
  --hidden-import=biomni.agent.react \
  --hidden-import=biomni.agent.qa_llm \
  --hidden-import=biomni.agent.function_generator \
  --hidden-import=biomni.agent.env_collection \
  --hidden-import=biomni.tool \
  --hidden-import=biomni.tool.biochemistry \
  --hidden-import=biomni.tool.bioengineering \
  --hidden-import=biomni.tool.bioimaging \
  --hidden-import=biomni.tool.biophysics \
  --hidden-import=biomni.tool.cancer_biology \
  --hidden-import=biomni.tool.cell_biology \
  --hidden-import=biomni.tool.database \
  --hidden-import=biomni.tool.genetics \
  --hidden-import=biomni.tool.genomics \
  --hidden-import=biomni.tool.glycoengineering \
  --hidden-import=biomni.tool.immunology \
  --hidden-import=biomni.tool.lab_automation \
  --hidden-import=biomni.tool.literature \
  --hidden-import=biomni.tool.microbiology \
  --hidden-import=biomni.tool.molecular_biology \
  --hidden-import=biomni.tool.pathology \
  --hidden-import=biomni.tool.pharmacology \
  --hidden-import=biomni.tool.physiology \
  --hidden-import=biomni.tool.protocols \
  --hidden-import=biomni.tool.support_tools \
  --hidden-import=biomni.tool.synthetic_biology \
  --hidden-import=biomni.tool.systems_biology \
  --hidden-import=biomni.tool.tool_registry \
  --hidden-import=biomni.know_how \
  --hidden-import=biomni.know_how.loader \
  --hidden-import=biomni.model \
  --hidden-import=biomni.model.retriever \
  --hidden-import=biomni.config \
  --hidden-import=biomni.llm \
  --hidden-import=biomni.utils \
  --hidden-import=api \
  --hidden-import=api.app \
  --hidden-import=api.websocket \
  --hidden-import=api.upload \
  --hidden-import=core \
  --hidden-import=core.config \
  --hidden-import=core.database \
  --hidden-import=core.security \
  --hidden-import=models \
  --hidden-import=models.models \
  --hidden-import=services \
  --hidden-import=services.agent_service \
  --hidden-import=services.callback \
  --hidden-import=services.config_service \
  --hidden-import=services.mock_agent \
  --hidden-import=uvicorn \
  --hidden-import=uvicorn.logging \
  --hidden-import=uvicorn.loops \
  --hidden-import=uvicorn.loops.auto \
  --hidden-import=uvicorn.protocols \
  --hidden-import=uvicorn.protocols.http \
  --hidden-import=uvicorn.protocols.http.auto \
  --hidden-import=uvicorn.protocols.websockets \
  --hidden-import=uvicorn.protocols.websockets.auto \
  --hidden-import=uvicorn.lifespan \
  --hidden-import=uvicorn.lifespan.on \
  --hidden-import=pymysql \
  --hidden-import=sqlalchemy.dialects.mysql.pymysql \
  --add-data "biomni/know_how/resource:biomni/know_how/resource" \
  --add-data "biomni/know_how/sgRNA_design_guide.md:biomni/know_how" \
  --add-data "biomni/know_how/single_cell_annotation.md:biomni/know_how" \
  --add-data "biomni/tool/schema_db:biomni/tool/schema_db" \
  --add-data "biomni/tool/protocols:biomni/tool/protocols" \
  --add-data "biomni/tool/tool_description:biomni/tool/tool_description" \
  --add-data "biomni/tool/example_mcp_tools:biomni/tool/example_mcp_tools" \
  main.py
```

产物在 `dist/biomni-agent/` 目录下，入口是 `dist/biomni-agent/biomni-agent`。

### 3. 验证

```bash
# 测试能否启动
./dist/biomni-agent/biomni-agent
# 应该看到 uvicorn 启动日志
# Ctrl+C 退出
```

### 4. 部署到 /opt/biomni/agent

```bash
# 清空旧的 agent 目录
sudo rm -rf /opt/biomni/agent/*

# 复制 PyInstaller 产物
sudo cp -r dist/biomni-agent/* /opt/biomni/agent/

# 设置权限
sudo chown -R biomni:biomni /opt/biomni/agent
sudo chmod -R 750 /opt/biomni/agent
sudo chmod 550 /opt/biomni/agent/biomni-agent
```

### 5. 修改 systemd service

```ini
# /etc/systemd/system/biomni-agent.service
[Unit]
Description=Biomni AI Agent
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=biomni
Group=biomni
WorkingDirectory=/opt/biomni/agent
EnvironmentFile=/opt/biomni/config/biomni.env
ExecStart=/opt/biomni/agent/biomni-agent
Restart=always
RestartSec=10
Environment="PYTHONUNBUFFERED=1"
StandardOutput=append:/opt/biomni/logs/agent.log
StandardError=append:/opt/biomni/logs/agent-error.log

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl restart biomni-agent
```

## 部署后的目录结构

```
/opt/biomni/agent/
├── biomni-agent              # 入口二进制（唯一可执行文件）
├── lib-dynload/              # Python C 扩展
├── biomni/                   # 打包后的数据文件
│   ├── know_how/resource/    # 资源文件
│   ├── tool/schema_db/*.pkl  # 数据文件
│   ├── tool/protocols/       # 协议文件
│   └── tool/tool_description/
└── ... (PyInstaller 运行时依赖)
```

没有任何 `.py` 文件，全部是编译后的二进制。

## 环境变量

Agent 不使用 `.env` 文件。所有配置通过 systemd `EnvironmentFile=/opt/biomni/config/biomni.env` 注入。

`biomni.env` 由 `first-boot.sh` 自动生成，包含：
- `JWT_SECRET_KEY` / `JWT_ALGORITHM`
- `DATABASE_URL`
- `USE_MOCK_AGENT`
- `AGENT_DATA_PATH` / `AGENT_UPLOAD_DATA_PATH`
- `CORS_ORIGINS`
- `SPRING_BOOT_URL`

## 常见问题

### hidden-import 不够导致运行时 ImportError

PyInstaller 静态分析可能漏掉动态 import 的模块。如果运行时报 `ModuleNotFoundError`，
在打包命令中加对应的 `--hidden-import=xxx` 重新打包。

### 数据文件找不到

PyInstaller 打包后，数据文件的路径会变。如果代码中用 `__file__` 定位数据文件，
需要改为用 `sys._MEIPASS`（PyInstaller 运行时解压目录）：

```python
import sys, os
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(__file__)
```

### 产物体积大

PyInstaller `--onedir` 产物通常 200-500MB（包含 Python 解释器和所有依赖）。
这是正常的，不影响运行性能。

### 不需要在 AMI 上安装 Python

PyInstaller 产物自带 Python 解释器，不依赖系统 Python。
但如果你还需要 venv 做其他事情，可以保留系统 Python。

## 文件权限加固

```bash
sudo chown -R biomni:biomni /opt/biomni/agent
sudo chmod -R 750 /opt/biomni/agent
sudo chmod 550 /opt/biomni/agent/biomni-agent
# ubuntu 用户无法读取 agent 目录
```

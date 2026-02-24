# Agent 构建指南（源码保护）

## 目标

将 Python Agent 的 `.py` 源文件编译为 `.so` 二进制文件，AMI 中不暴露可读源码。

## 前提条件

必须在与 AMI 相同的平台上编译：
- Ubuntu 22.04 x86_64
- Python 3.11
- 建议直接在 EC2 Golden Instance 上操作

## 步骤

### 1. 在 EC2 上安装编译依赖

```bash
sudo apt install -y python3.11-dev gcc
```

### 2. 创建编译用 venv

```bash
cd /opt/biomni/agent
sudo -u biomni python3.11 -m venv venv
sudo -u biomni venv/bin/pip install --upgrade pip
sudo -u biomni venv/bin/pip install cython setuptools
sudo -u biomni venv/bin/pip install -r requirements-api.txt
# 安装 biomni 包的依赖（pydantic, langchain, python-dotenv 等）
sudo -u biomni venv/bin/pip install -e .
```

### 3. 创建编译脚本

```bash
cat > /opt/biomni/agent/setup_cython.py << 'PYEOF'
from setuptools import setup
from Cython.Build import cythonize
import glob
import os

# 需要编译的目录
COMPILE_DIRS = ['api', 'core', 'services', 'models', 'biomni']

py_files = []
for d in COMPILE_DIRS:
    if os.path.isdir(d):
        py_files.extend(glob.glob(f'{d}/**/*.py', recursive=True))

# 保留 __init__.py（维持包结构）和 main.py（入口）
py_files = [f for f in py_files
            if '__init__' not in f
            and f != 'main.py'
            and '__pycache__' not in f]

print(f"Will compile {len(py_files)} files:")
for f in sorted(py_files):
    print(f"  {f}")

setup(
    ext_modules=cythonize(
        py_files,
        compiler_directives={'language_level': "3"},
        nthreads=4,
    ),
)
PYEOF
```

### 4. 执行编译

```bash
cd /opt/biomni/agent
sudo -u biomni venv/bin/python setup_cython.py build_ext --inplace
```

编译成功后，每个 `.py` 文件旁边会生成对应的 `.so` 文件，例如：
```
api/app.cpython-311-x86_64-linux-gnu.so
biomni/agent/a1.cpython-311-x86_64-linux-gnu.so
core/config.cpython-311-x86_64-linux-gnu.so
```

### 5. 删除源文件，只保留 .so

```bash
cd /opt/biomni/agent

# 删除已编译的 .py 文件（保留 __init__.py 和 main.py）
for dir in api core services models biomni; do
    if [ -d "$dir" ]; then
        find "$dir" -name "*.py" ! -name "__init__.py" -delete
    fi
done

# 删除 Cython 中间文件
find . -name "*.c" -delete
rm -rf build/
rm -f setup_cython.py

# 删除不需要的文件
rm -rf tutorials/ docs/ figs/ biomni_env/
rm -f debug_agent_output.py diagnose_steps.py test_callback.py
rm -f verify_fix.sh start.sh stop.sh
rm -f .env .env.example .DS_Store
rm -f CONTRIBUTION.md DETAILS.md LOGGING_GUIDE.md A1_CONFIGURATION_GUIDE.md
rm -f README.md MANIFEST.in license_info.md

# 删除所有 __pycache__
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete
```

### 6. 验证

```bash
cd /opt/biomni/agent

# 检查残留的 .py 文件（应该只有 __init__.py 和 main.py）
echo "=== Remaining .py files ==="
find . -name "*.py" | sort

# 应该输出类似：
# ./main.py
# ./api/__init__.py
# ./biomni/__init__.py
# ./biomni/agent/__init__.py
# ./biomni/tool/__init__.py
# ./core/__init__.py
# ./models/__init__.py
# ./services/__init__.py

# 验证 import 正常
sudo -u biomni venv/bin/python -c "from api.app import app; print('OK: api.app')"
sudo -u biomni venv/bin/python -c "from core.config import settings; print('OK: core.config')"
```

### 7. 编译后的目录结构

```
/opt/biomni/agent/
├── main.py                                         # 入口（保留）
├── pyproject.toml                                   # 包定义（保留）
├── requirements-api.txt                             # 依赖列表（保留）
├── LICENSE                                          # 许可证（保留）
├── venv/                                            # Python 虚拟环境
├── api/
│   ├── __init__.py
│   ├── app.cpython-311-x86_64-linux-gnu.so
│   ├── websocket.cpython-311-x86_64-linux-gnu.so
│   └── upload.cpython-311-x86_64-linux-gnu.so
├── biomni/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── a1.cpython-311-x86_64-linux-gnu.so      # 核心算法
│   │   └── react.cpython-311-x86_64-linux-gnu.so
│   ├── tool/
│   │   ├── __init__.py
│   │   ├── *.so                                     # 所有工具
│   │   ├── schema_db/*.pkl                          # 数据文件（保留）
│   │   ├── protocols/                               # 协议文件（保留）
│   │   └── tool_description/*.so
│   ├── know_how/
│   │   ├── __init__.py
│   │   ├── *.so
│   │   └── resource/                                # 资源文件（保留）
│   └── model/
│       ├── __init__.py
│       └── *.so
├── core/
│   ├── __init__.py
│   └── *.so
├── models/
│   ├── __init__.py
│   └── *.so
└── services/
    ├── __init__.py
    └── *.so
```

## 环境变量

Agent 不再使用自己的 `.env` 文件。所有配置通过 systemd 的 `EnvironmentFile` 注入：

```ini
# /etc/systemd/system/biomni-agent.service
[Service]
EnvironmentFile=/opt/biomni/config/biomni.env
```

`biomni.env` 由 `first-boot.sh` 自动生成，包含 Agent 需要的所有变量：
- `JWT_SECRET_KEY` / `JWT_ALGORITHM`
- `DATABASE_URL`
- `USE_MOCK_AGENT`
- `AGENT_DATA_PATH` / `AGENT_UPLOAD_DATA_PATH`
- `CORS_ORIGINS`
- `SPRING_BOOT_URL`

Agent 的 `core/config.py`（Pydantic Settings）会自动从环境变量读取这些值。

## 注意事项

1. **不要用 `pip install -e .`**：editable install 依赖 `.py` 源文件，删除后会 import 失败。
   systemd 的 `WorkingDirectory=/opt/biomni/agent` 会让 Python 自动在 CWD 找到包。

2. **Python 版本必须一致**：`.so` 文件名包含 `cpython-311`，只能在 Python 3.11 上运行。

3. **某些模块可能编译失败**：如果遇到 Cython 不支持的语法（如某些动态 import），
   可以跳过那些文件，保留 `.py`。在 `setup_cython.py` 中排除：
   ```python
   SKIP_FILES = ['biomni/some_module.py']
   py_files = [f for f in py_files if f not in SKIP_FILES]
   ```

4. **数据文件不受影响**：`.pkl`、`.csv`、`.txt`、`.md` 等数据文件保持原样。

5. **如果 Cython 方案不可行**，回退到 PyInstaller：
   ```bash
   pip install pyinstaller
   pyinstaller --onedir \
     --hidden-import=biomni --hidden-import=biomni.agent \
     --hidden-import=biomni.tool --hidden-import=biomni.know_how \
     --add-data "biomni/know_how:biomni/know_how" \
     --add-data "biomni/tool/schema_db:biomni/tool/schema_db" \
     --add-data "biomni/tool/protocols:biomni/tool/protocols" \
     --name biomni-agent main.py
   ```
   然后 systemd 改为：
   ```ini
   ExecStart=/opt/biomni/agent/dist/biomni-agent/biomni-agent
   ```

## 文件权限加固

```bash
sudo chown -R biomni:biomni /opt/biomni/agent
sudo chmod -R 750 /opt/biomni/agent
find /opt/biomni/agent -name "*.so" -exec chmod 550 {} \;
# ubuntu 用户无法读取 agent 目录
```

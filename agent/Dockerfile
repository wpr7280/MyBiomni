# ============================================================
# Stage 1: 安装依赖 + 编译 .pyc
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /app

# 安装依赖
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY pyproject.toml .
COPY biomni/ biomni/
COPY api/ api/
COPY core/ core/
COPY models/ models/
COPY services/ services/
COPY main.py .

# 安装 biomni 包
RUN pip install --no-cache-dir .

# 编译所有 .py 为 .pyc
RUN python -m compileall -b -f api/ core/ models/ services/ biomni/ main.py

# 删除 .py 源文件（保留 __init__.py 的 .pyc）
RUN find api/ core/ models/ services/ biomni/ -name "*.py" -delete
RUN rm -f main.py

# ============================================================
# Stage 2: 最终镜像（只有 .pyc + 数据文件）
# ============================================================
FROM python:3.11-slim

WORKDIR /app

# 从 builder 复制已安装的 Python 包
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制编译后的 .pyc 文件
COPY --from=builder /app/api/ api/
COPY --from=builder /app/core/ core/
COPY --from=builder /app/models/ models/
COPY --from=builder /app/services/ services/
COPY --from=builder /app/biomni/ biomni/
COPY --from=builder /app/main.pyc .

# 复制数据文件（这些不需要编译）
COPY biomni/know_how/resource/ biomni/know_how/resource/
COPY biomni/know_how/*.md biomni/know_how/
COPY biomni/tool/schema_db/ biomni/tool/schema_db/
COPY biomni/tool/protocols/ biomni/tool/protocols/
COPY biomni/tool/tool_description/ biomni/tool/tool_description/
COPY biomni/tool/example_mcp_tools/ biomni/tool/example_mcp_tools/

# 创建非 root 用户
RUN useradd -r -s /usr/sbin/nologin biomni
USER biomni

EXPOSE 8000

CMD ["python", "main.pyc"]

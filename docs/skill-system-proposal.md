# WarpHelix Skill 文件化系统 — 需求分析与方案设计

## 1. 背景与动机

### 1.1 现状

当前 WarpHelix Agent 的能力由以下部分组成：

| 组件 | 位置 | 形态 | 问题 |
|------|------|------|------|
| **Tool 实现** | `biomni/tool/*.py` | 24 个 Python 模块，共 32K+ 行 | 纯代码，生信专家无法维护 |
| **Tool 描述** | `biomni/tool/tool_description/*.py` | Python dict 描述 name/params | 与实现分离但也是代码文件 |
| **Know-How** | `biomni/know_how/*.md` | 2 个 Markdown 文件 | 数量太少，未成体系 |
| **Tool Registry** | `biomni/tool/tool_registry.py` | 内存注册表 | 不支持动态增删，无持久化管理 |
| **Tool Retriever** | `biomni/model/retriever.py` | LLM prompt-based 选择 | 从全量工具中挑选，无 skill 分组概念 |

### 1.2 核心痛点

1. **生信专家无法参与维护**：添加/修改一个工具需要写 Python 代码、理解 LangChain schema、部署服务，门槛太高
2. **Know-How 与 Tool 脱节**：分析流程指导（how-to）和工具定义分开管理，agent 无法将流程知识和工具能力关联
3. **扩展不灵活**：新增领域能力需要改代码、改 `read_module2api()` 的 fields 列表、重新部署
4. **无管理界面**：没有可视化的方式查看、编辑、启用/禁用工具和知识

### 1.3 目标

- 生信专家能通过编写/编辑文件（或后台界面）独立维护 agent 的能力
- Tool 和 Know-How 统一为 **Skill**，作为 agent 能力的基本单元
- 支持热加载，无需重启服务即可生效
- 保持与现有 Tool 体系的向后兼容，可渐进迁移

---

## 2. 概念模型

### 2.1 什么是 Skill

**Skill = Know-How（知道怎么做）+ Tool（具体能做什么）+ Metadata（管理信息）**

一个 Skill 是 agent 在某个具体生物学场景下的完整能力包，包含：

```
skill/
├── skill.yaml          # Skill 元数据与配置（必需）
├── how_to.md           # 分析流程指导文档（必需）
├── tools/              # 工具定义（可选，可引用已有工具）
│   ├── tool_1.yaml     # 工具描述
│   └── tool_2.yaml
├── templates/          # 代码模板（可选）
│   └── pipeline.py
└── resources/          # 参考数据/文件（可选）
    └── reference.csv
```

### 2.2 Skill 与现有概念的映射

| 新概念 | 对应现有组件 | 说明 |
|--------|-------------|------|
| `skill.yaml` | `tool_description/*.py` 的 dict | 结构化描述，但用 YAML 更易编辑 |
| `how_to.md` | `know_how/*.md` | 分析流程指导，但与 skill 绑定 |
| `tools/*.yaml` | `tool/*.py` 中的函数 | 工具的声明式描述 |
| `templates/*.py` | `tool/*.py` 中的函数体 | 可执行代码模板 |

### 2.3 Skill 的粒度

推荐粒度：**一个 skill = 一个分析场景**，而非一个函数。

示例：
- ✅ `single_cell_annotation` — 包含多个工具（popv、celltypist、panhumanpy 等）+ 流程指导
- ✅ `sgrna_design` — 包含 sgRNA 设计相关工具 + 设计指南
- ❌ `annotate_celltype_scRNA` — 粒度太细，应该是 skill 内的一个 tool

---

## 3. Skill 文件格式规范

### 3.1 skill.yaml（Skill 元数据）

```yaml
# 基础信息
name: single_cell_annotation
display_name: 单细胞 RNA-seq 细胞类型注释
version: "1.0.0"
category: single_cell       # 学科分类
description: >
  对单细胞 RNA-seq 数据进行细胞类型注释，支持多种注释方法
  （popV、CellTypist、Azimuth 等），可处理人类和小鼠数据。

# 作者与许可
authors:
  - name: "张三"
    role: "maintainer"
license: "MIT"
commercial_use: true

# 依赖
dependencies:
  python_packages:
    - scanpy>=1.9
    - anndata>=0.8
    - popv>=0.8
    - celltypist>=1.3
    - panhumanpy>=0.1
  data_lake:
    - celltype_markers.csv
    - tissue_ontology.json

# 工具列表（引用本 skill 内的 tools/*.yaml）
tools:
  - annotate_celltype_scRNA
  - annotate_celltype_with_panhumanpy
  - unsupervised_celltype_transfer

# 适用场景（帮助 retriever 匹配）
triggers:
  - 细胞类型注释
  - cell type annotation
  - 单细胞聚类后注释
  - scRNA-seq cell type
  - 细胞类型鉴定
  - cluster annotation

# 状态控制
enabled: true
```

### 3.2 how_to.md（分析流程指导）

```markdown
# 单细胞 RNA-seq 细胞类型注释指南

## 前置条件
- 已完成质控、标准化、降维、聚类的 AnnData 对象
- 数据格式：.h5ad 文件

## 推荐流程

### 步骤 1：数据检查
检查聚类结果是否合理，确认 leiden/louvain 聚类已完成。

### 步骤 2：选择注释方法
根据数据类型选择合适的方法：
- **有参考数据集** → 使用 `unsupervised_celltype_transfer`（popV）
- **人类数据** → 使用 `annotate_celltype_with_panhumanpy`（Azimuth）
- **通用场景** → 使用 `annotate_celltype_scRNA`（LLM + marker genes）

### 步骤 3：执行注释
调用对应工具，传入正确参数。

### 步骤 4：结果验证
- 检查注释结果分布
- 对比已知 marker genes
- 生成 UMAP 可视化

## 注意事项
- popV 需要参考数据集，确保 ref 和 query 的基因名格式一致
- Azimuth 仅支持人类数据
- LLM 注释依赖 marker gene 质量，建议检查 DEG 结果
```

### 3.3 tools/tool_name.yaml（工具定义）

```yaml
name: annotate_celltype_scRNA
display_name: LLM 驱动的细胞类型注释
description: >
  基于 leiden 聚类的差异表达基因，使用 LLM 推断细胞类型。
  支持结合参考数据集的转移标签进行综合判断。

# 参数定义
parameters:
  required:
    - name: adata_filename
      type: str
      description: AnnData 文件名
    - name: data_dir
      type: str
      description: 数据文件所在目录
    - name: data_info
      type: str
      description: 数据基本信息（物种、组织、状态等）
    - name: data_lake_path
      type: str
      description: Data lake 路径
  optional:
    - name: cluster
      type: str
      default: "leiden"
      description: 聚类方法名
    - name: llm
      type: str
      default: "claude-sonnet-4-5"
      description: 使用的 LLM 模型

# 返回值
returns:
  type: str
  description: 注释结果摘要和输出文件路径

# 实现引用
implementation:
  module: biomni.tool.genomics        # 引用已有 Python 模块
  function: annotate_celltype_scRNA   # 引用已有函数

# 或者：内联代码模板（二选一）
# implementation:
#   type: template
#   file: templates/annotate_celltype.py
```

---

## 4. 系统架构

### 4.1 整体架构

```
┌─────────────────────────────────────────────────────┐
│                   Admin Frontend                     │
│            Skill 管理界面（CRUD + 预览）              │
└────────────────────────┬────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────┐
│                   Backend API                        │
│              /api/skills/* endpoints                 │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│               SkillManager (核心)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐    │
│  │ SkillStore│ │SkillLoader│ │SkillRetriever    │    │
│  │(持久化)   │ │(文件解析)  │ │(检索匹配)        │    │
│  └──────────┘ └──────────┘ └──────────────────┘    │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│                skills/ 目录                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │single_cell_ │ │sgrna_design/│ │pharmacology_│   │
│  │annotation/  │ │             │ │screening/   │   │
│  │ skill.yaml  │ │ skill.yaml  │ │ skill.yaml  │   │
│  │ how_to.md   │ │ how_to.md   │ │ how_to.md   │   │
│  │ tools/      │ │ tools/      │ │ tools/      │   │
│  └─────────────┘ └─────────────┘ └─────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 4.2 核心模块

#### SkillStore（持久化层）

负责 skill 文件的读写和版本管理：
- 读取 `skills/` 目录下所有 skill
- 支持 CRUD 操作
- 可选：与数据库同步元数据（便于搜索和管理）
- 可选：Git 版本控制

#### SkillLoader（加载层）

替代现有的 `KnowHowLoader` + `read_module2api()`：
- 解析 `skill.yaml` → 结构化 Skill 对象
- 解析 `how_to.md` → 注入 agent system prompt
- 解析 `tools/*.yaml` → 生成 LangChain Tool 对象
- 支持热加载（文件变更时自动重新加载）

#### SkillRetriever（检索层）

增强现有的 `ToolRetriever`：
- 从"工具级检索"升级为"Skill 级检索"
- 先匹配相关 Skill，再加载 Skill 内的工具和 how-to
- 利用 `triggers` 字段提高匹配准确度
- 保留 LLM-based retrieval 作为 fallback

### 4.3 与现有系统的集成

```
现有流程:
  User Query → ToolRetriever → 选择 Tools → Agent(ReAct/A1) → 执行

新流程:
  User Query → SkillRetriever → 匹配 Skills
                                  ├── 加载 how_to.md → 注入 system prompt
                                  ├── 加载 tools → 绑定到 LLM
                                  └── 加载 dependencies → （未来）sandbox 准备
             → Agent(ReAct/A1) → 执行
```

**关键设计**：Agent 层（A1/react）几乎不需要改动，改动集中在"给 agent 准备什么工具和上下文"这一层。

---

## 5. 迁移方案

### 5.1 迁移策略：渐进式，双轨并行

不一次性替换，而是：
1. 新建 `skills/` 目录，新增能力用 skill 文件方式
2. 现有 `tool/*.py` + `tool_description/*.py` 继续工作
3. SkillLoader 同时加载两种来源
4. 逐步将现有 tool 迁移为 skill（按优先级/需求）

### 5.2 现有 Tool 模块 → Skill 的映射建议

| 现有模块 | 建议拆分的 Skill | 优先级 |
|---------|-----------------|--------|
| `genomics.py` (2759行, 多个功能) | `single_cell_annotation`, `gene_expression_analysis`, `variant_analysis` | 🔴 高 |
| `molecular_biology.py` (2222行) | `sequence_analysis`, `protein_structure`, `cloning_design` | 🟡 中 |
| `pharmacology.py` (4282行) | `drug_screening`, `pharmacokinetics`, `target_identification` | 🟡 中 |
| `database.py` (4974行) | `biodata_query`（通用查询能力，可作为跨 skill 共享工具） | 🔴 高 |
| `genetics.py` (1672行) | `sgrna_design`, `crispr_analysis`, `genetic_variant` | 🔴 高 |
| `immunology.py` (1972行) | `immune_repertoire`, `antigen_prediction` | 🟡 中 |
| 其余模块 | 按需迁移 | 🟢 低 |

### 5.3 Tool Implementation 的处理

**核心问题**：现有 tool 的实现（Python 函数）怎么处理？

**方案：三种实现模式共存**

```yaml
# 模式 1：引用已有模块（迁移期主要使用）
implementation:
  type: module_ref
  module: biomni.tool.genomics
  function: annotate_celltype_scRNA

# 模式 2：代码模板（新增 skill 推荐使用，配合 sandbox）
implementation:
  type: template
  file: templates/pipeline.py
  sandbox: true  # 在 sandbox 中执行

# 模式 3：纯指导型（无具体工具，仅提供 how-to 让 agent 用通用工具完成）
implementation:
  type: guidance_only  # agent 结合 run_python_repl 自行编码
```

迁移期间大量使用模式 1（引用已有函数），等 sandbox 就绪后逐步迁移到模式 2。

---

## 6. Admin 管理界面

### 6.1 功能需求

| 功能 | 说明 | 优先级 |
|------|------|--------|
| **Skill 列表** | 按分类查看所有 skill，显示状态/版本/作者 | P0 |
| **Skill 详情** | 查看 skill.yaml + how_to.md 内容 | P0 |
| **启用/禁用** | 一键切换 skill 的 enabled 状态 | P0 |
| **编辑 how_to.md** | Markdown 编辑器，支持预览 | P0 |
| **编辑 skill.yaml** | 表单式编辑元数据 | P1 |
| **新建 Skill** | 向导式创建，自动生成目录结构 | P1 |
| **编辑 tool 定义** | 编辑 tools/*.yaml | P1 |
| **删除 Skill** | 软删除（标记 disabled）| P1 |
| **版本历史** | 查看修改记录（依赖 Git）| P2 |
| **导入/导出** | 打包下载/上传 skill 目录 | P2 |

### 6.2 界面原型

```
┌────────────────────────────────────────────────────┐
│  Skills Management                    [+ New Skill] │
├──────────┬─────────────────────────────────────────┤
│ Filter:  │                                         │
│ □ All    │  single_cell_annotation          v1.0.0 │
│ □ SC     │  ✅ Enabled | single_cell | 张三        │
│ □ Genomic│  3 tools | Updated 2026-04-01           │
│ □ Pharma │─────────────────────────────────────────│
│ □ ...    │  sgrna_design                    v1.2.0 │
│          │  ✅ Enabled | genetics | 李四            │
│          │  2 tools | Updated 2026-03-28           │
│          │─────────────────────────────────────────│
│          │  drug_screening                  v0.9.0 │
│          │  ⛔ Disabled | pharmacology | 王五       │
│          │  5 tools | Updated 2026-03-15           │
└──────────┴─────────────────────────────────────────┘
```

点击进入详情：

```
┌────────────────────────────────────────────────────┐
│  ← Back   single_cell_annotation        [Save]     │
├──────────┬─────────────────────────────────────────┤
│ Overview │  Name: single_cell_annotation            │
│ How-To   │  Display: 单细胞 RNA-seq 细胞类型注释     │
│ Tools    │  Category: single_cell                   │
│ Settings │  Version: 1.0.0                          │
│          │  Status: ✅ Enabled [Toggle]              │
│          │                                          │
│          │  Description:                            │
│          │  对单细胞 RNA-seq 数据进行细胞类型注释...   │
│          │                                          │
│          │  Dependencies:                           │
│          │  scanpy>=1.9, anndata>=0.8, popv>=0.8    │
│          │                                          │
│          │  Tools (3):                              │
│          │  • annotate_celltype_scRNA               │
│          │  • annotate_celltype_with_panhumanpy     │
│          │  • unsupervised_celltype_transfer        │
└──────────┴─────────────────────────────────────────┘
```

---

## 7. API 设计

### 7.1 Skill 管理 API

```
GET    /api/skills                    # 列表（支持 ?category=&enabled=&search= 过滤）
GET    /api/skills/:id                # 详情
POST   /api/skills                    # 创建
PUT    /api/skills/:id                # 更新元数据
PATCH  /api/skills/:id/enable         # 启用
PATCH  /api/skills/:id/disable        # 禁用
DELETE /api/skills/:id                # 删除

GET    /api/skills/:id/how-to         # 获取 how-to 内容
PUT    /api/skills/:id/how-to         # 更新 how-to 内容

GET    /api/skills/:id/tools          # 获取 skill 内的工具列表
GET    /api/skills/:id/tools/:tool_id # 获取工具详情
PUT    /api/skills/:id/tools/:tool_id # 更新工具定义

GET    /api/skills/categories         # 获取所有分类
POST   /api/skills/:id/reload         # 热加载单个 skill
POST   /api/skills/reload-all         # 热加载所有 skill
```

### 7.2 与 Agent 的集成 API（内部）

```python
class SkillManager:
    def get_enabled_skills(self) -> List[Skill]
    def retrieve_skills(self, query: str, top_k: int = 5) -> List[Skill]
    def get_skill_tools(self, skill_id: str) -> List[LangChainTool]
    def get_skill_howto(self, skill_id: str) -> str
    def get_skill_dependencies(self, skill_id: str) -> List[str]
    def reload_skill(self, skill_id: str) -> None
    def reload_all(self) -> None
```

---

## 8. 实施计划

### Phase 1：基础框架（第 1-2 周）

**目标**：搭建 Skill 文件格式和加载体系，跑通最小闭环

- [ ] 定义 `skill.yaml` / `how_to.md` / `tools/*.yaml` 的 JSON Schema
- [ ] 实现 `SkillLoader`：解析 skill 目录 → Skill 对象
- [ ] 实现 `SkillManager`：管理所有 skill 的生命周期
- [ ] 将现有 2 个 know-how 文件迁移为 skill 格式（`sgrna_design`、`single_cell_annotation`）
- [ ] 在 A1 agent 中集成 SkillManager，`how_to.md` 注入 system prompt
- [ ] 验证：agent 使用新 skill 格式的 how-to + 现有 tool 执行任务

**交付物**：
- `biomni/skill/` 模块（loader, manager, models）
- `skills/` 目录 + 2 个示例 skill
- A1 agent 兼容 skill 系统

### Phase 2：Tool 声明式定义（第 3-4 周）

**目标**：Tool 从代码定义变为 YAML 声明式定义

- [ ] 实现 `tools/*.yaml` → LangChain Tool 的转换器
- [ ] 支持 `implementation.type: module_ref`（引用已有 Python 函数）
- [ ] 改造 SkillRetriever：先匹配 skill 再加载 tool
- [ ] 迁移 3-5 个高优先级模块（genomics、genetics、database 的部分功能）
- [ ] 保持 fallback：未迁移的 tool 仍通过旧路径加载

**交付物**：
- tool YAML → LangChain Tool 转换逻辑
- SkillRetriever（升级版检索）
- 5+ 个可用 skill

### Phase 3：Admin 管理界面（第 5-6 周）

**目标**：生信专家可通过界面管理 skill

- [ ] 后端 API：Skill CRUD + how-to 编辑 + 启用/禁用
- [ ] 前端页面：Skill 列表 + 详情 + Markdown 编辑器
- [ ] 热加载：修改后无需重启即可生效
- [ ] 权限控制：区分管理员和普通用户

**交付物**：
- `/api/skills/*` REST API
- Admin 前端 Skill 管理页面
- 热加载机制

### Phase 4：完善与优化（第 7-8 周）

**目标**：全面迁移 + 高级特性

- [ ] 迁移剩余 tool 模块为 skill 格式
- [ ] 支持 `implementation.type: template`（代码模板执行，为 sandbox 做准备）
- [ ] Skill 导入/导出功能
- [ ] 版本管理（Git 集成）
- [ ] 文档和培训材料

---

## 9. 风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| 现有 tool 函数有复杂依赖和副作用 | 迁移困难 | Phase 2 先用 module_ref 引用，不改实现 |
| Skill 格式设计不合理需要返工 | 延期 | Phase 1 只做 2 个示例，快速验证后再批量迁移 |
| Agent 性能下降（多了一层 skill 解析） | 体验 | SkillLoader 做缓存，只在文件变更时重新解析 |
| 生信专家不会写 YAML | 推广难 | Admin 界面用表单编辑，屏蔽 YAML 细节 |
| 热加载导致运行中的 agent 出问题 | 稳定性 | 热加载只影响新会话，进行中的会话用旧配置 |

---

## 10. 成本估算

| 阶段 | 工作量 | 前置依赖 |
|------|--------|---------|
| Phase 1 基础框架 | 1 人 × 2 周 | 无 |
| Phase 2 Tool 声明式 | 1 人 × 2 周 | Phase 1 |
| Phase 3 Admin 界面 | 1 前端 + 1 后端 × 2 周 | Phase 1 |
| Phase 4 完善优化 | 1 人 × 2 周 | Phase 2 + 3 |

**总计**：约 8 周（1-2 人），Phase 1 完成后即可用。

---

## 附录 A：完整 Skill 示例

```
skills/
└── single_cell_annotation/
    ├── skill.yaml
    ├── how_to.md
    ├── tools/
    │   ├── annotate_celltype_scRNA.yaml
    │   ├── annotate_celltype_with_panhumanpy.yaml
    │   └── unsupervised_celltype_transfer.yaml
    └── resources/
        └── celltype_markers_reference.csv
```

## 附录 B：与 DeerFlow 2.0 的对比

| 特性 | DeerFlow 2.0 | WarpHelix Skill 系统 |
|------|-------------|---------------------|
| Skill 格式 | Markdown + YAML | YAML + Markdown |
| 工具注册 | 动态，plugin 式 | 声明式 YAML + 引用已有代码 |
| Sub-agent | 内置多 agent 编排 | 暂不需要，保持单 agent |
| Sandbox | 内置 Docker sandbox | 未来 Phase 5 加入 |
| 领域特化 | 通用框架 | 生物信息学深度定制 |
| 管理界面 | Web UI | Admin 后台集成 |

**借鉴了 DeerFlow 的**：Skill 文件化思想、声明式工具定义、能力与实现分离
**未采用的**：多 agent 编排（当前场景不需要）、完整框架迁移（成本太高）

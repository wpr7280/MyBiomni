# 单细胞 RNA-seq 细胞类型注释指南

## 前置条件

- 已完成质控、标准化、降维、聚类的 AnnData 对象（`.h5ad` 文件）
- leiden/louvain 聚类已完成
- 已去除 doublet 和低质量细胞

## 推荐流程

### 步骤 1：数据检查

检查聚类结果是否合理，确认以下内容：
- leiden/louvain 聚类已完成
- 聚类分辨率适当（不过度聚类也不欠聚类）
- doublet 已移除（推荐 Scrublet / DoubletFinder）

### 步骤 2：选择注释方法

根据数据类型和可用资源选择合适的方法：

| 场景 | 推荐工具 | 说明 |
|------|---------|------|
| 有参考数据集 | `unsupervised_celltype_transfer` (popV) | 基于 scANVI 的半监督标签转移 |
| 人类数据（通用） | `annotate_celltype_with_panhumanpy` (Azimuth) | Panhuman Azimuth 神经网络，提供层次化标签 |
| 通用场景 / 需要 LLM 推理 | `annotate_celltype_scRNA` | 基于 DEG + LLM 推断细胞类型 |

**建议**：如果条件允许，使用多种方法交叉验证。

### 步骤 3：执行注释

#### 方法 A：LLM 驱动注释（`annotate_celltype_scRNA`）

适用于大多数场景，基于 leiden 聚类的差异表达基因，使用 LLM 推断细胞类型。

- 必需参数：`adata_filename`, `data_dir`, `data_info`, `data_lake_path`
- 可选：`cluster`（默认 "leiden"），`llm`，`composition`（转移标签结果）
- **提示**：如果先用 popV 获得了转移标签，可通过 `composition` 参数传入以辅助判断

#### 方法 B：Panhuman Azimuth（`annotate_celltype_with_panhumanpy`）

仅限人类数据，提供层次化细胞类型标签。

- 必需参数：`adata_path`
- 可选：`feature_names_col`, `refine`（标签细化），`umap`（生成嵌入和 UMAP）

#### 方法 C：popV 标签转移（`unsupervised_celltype_transfer`）

需要已标注的参考数据集，使用 scANVI 等方法进行半监督标签转移。

- 必需参数：`path_to_annotated_h5ad`, `path_to_not_annotated_h5ad`, `ref_labels_key`
- 可选：`query_batch_key`, `ref_batch_key`, 以及多种注释方法开关（CELLTYPIST, KNN_HARMONY, SCANVI_POPV 等）
- **注意**：默认仅启用 SCANVI_POPV，可根据需要启用更多方法，但每增加一种会增加计算量

### 步骤 4：结果验证

- 检查注释结果的分布是否合理
- 对比已知 marker genes（参见下方参考列表）
- 生成 UMAP 可视化确认空间分布
- 跨方法对比：手动注释和自动注释结果应基本一致

## 常见 Marker Genes 参考

### 血液/免疫细胞
- **T cells**: CD3D, CD3E; CD4, CD8A（亚型）
- **B cells**: CD19, MS4A1 (CD20), CD79A
- **Monocytes/Macrophages**: CD14, CD68, LYZ
- **NK cells**: NCAM1 (CD56), NKG7, KLRD1
- **Dendritic cells**: FCER1A, CD1C

### 上皮细胞
- **General epithelial**: EPCAM, KRT18, KRT19
- **Lung AT1**: AGER, PDPN
- **Lung AT2**: SFTPC, SFTPA1

### 基质细胞
- **Fibroblasts**: COL1A1, DCN, LUM
- **Endothelial**: PECAM1 (CD31), VWF, CDH5
- **Smooth muscle**: ACTA2, MYH11, TAGLN

## 注意事项

1. **popV** 需要参考数据集，确保 ref 和 query 的基因名格式一致
2. **Azimuth (panhumanpy)** 仅支持人类数据
3. **LLM 注释** 依赖 marker gene 质量，建议先检查 DEG 结果
4. 不要过度聚类——太细的聚类会产生人为的细胞类型区分
5. 不要混淆细胞状态（activated vs resting）和细胞类型
6. 建议始终使用多种方法交叉验证结果

## 常见问题排查

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 所有 cluster 看起来相似 | 分辨率太低 / 未标准化 | 提高聚类分辨率，检查归一化 |
| 太多小 cluster | 分辨率太高 | 降低分辨率，合并相似 cluster |
| 自动注释结果不一致 | 输入未标准化 | 检查输入格式，尝试多种工具 |
| 参考转移失败 | 批次效应 / 基因集不匹配 | 检查 batch correction，确认基因名重叠 |

## 参考资源

- [Scanpy](https://scanpy.readthedocs.io/)
- [CellTypist](https://www.celltypist.org/)
- [scArches](https://scarches.readthedocs.io/)
- [PanglaoDB](https://panglaodb.se/) — Marker gene 数据库
- [CellMarker](http://xteam.xbio.top/CellMarker/) — 细胞 Marker 数据库

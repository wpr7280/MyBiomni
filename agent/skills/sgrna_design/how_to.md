# sgRNA 设计指南：三层策略

## 概述

本指南提供三层递进的 sgRNA 设计策略，**始终从 Option 1 开始**，仅在前一层无法满足需求时才进入下一层。

## 设计流程

### Option 1：查找已验证的 sgRNA 序列（推荐优先）

**必须完成 Method 1 和 Method 2 两种方法后，才能进入 Option 2。**

#### Method 1：搜索本地数据库（最快）

我们维护了来自 Addgene 的 300+ 条已验证 sgRNA 序列数据库。

- **位置**：`biomni/know_how/resource/addgene_grna_sequences.csv`
- **搜索字段**：Target_Gene, Target_Species, Application (cut/activate/RNA targeting), Cas9_Species
- **关键输出**：Target_Sequence (20bp), Plasmid_ID, PubMed_ID

#### Method 2：文献 Web 搜索（必须执行）

即使 Method 1 未找到结果，也必须用 `advanced_web_search_claude` 进行文献搜索。

推荐搜索模式：
- `"sgRNA" OR "guide RNA" "[GENE_NAME]" validated experimental`
- `"CRISPR knockout" "[GENE_NAME]" sgRNA sequence validated`
- `"[GENE_NAME]" sgRNA "cutting efficiency" OR "on-target"`

**如果找到匹配结果**：记录序列、参考文献、验证详情，任务完成。

**如果两种方法都未找到**：进入 Option 2。

### Option 2：下载 CRISPick 预计算 sgRNA

使用 Broad Institute GPP 的 CRISPick 预计算数据集（238 个数据集）。

#### 关键步骤

1. **查找下载链接**：从 `biomni/know_how/resource/CRISPick_download_links.txt` 搜索
2. **文件命名规则**：`sgRNA_design_{TAXID}_{GENOME}_{CAS}_{APPLICATION}_{ALGORITHM}_{SOURCE}_{DATE}.txt.gz`
3. **常用数据集**：
   - 人类 SpCas9 Knockout: `9606_GRCh38_SpyoCas9_CRISPRko`
   - 人类 SpCas9 Activation: `9606_GRCh38_SpyoCas9_CRISPRa`
   - 小鼠 SpCas9 Knockout: `10090_GRCm38_SpyoCas9_CRISPRko`

4. **选择 sgRNA**：
   - 默认按 `Combined Rank` 排序（平衡效率和特异性）
   - 可按 `On-Target Rank`（效率优先）或 `Off-Target Rank`（特异性优先）排序
   - 可按外显子号、基因组位置、Target Cut % 等进一步过滤

5. **选择 3-4 条 sgRNA**（来自不同外显子以增加冗余性）

⚠️ **重要**：AsCas12a 和 enAsCas12a 是**不同的酶**，设计不可互换！

**如果数据集不覆盖目标基因/物种**：进入 Option 3。

### Option 3：从头设计 sgRNA（最后手段）

#### 基本设计规则

| 参数 | SpCas9 | SaCas9 | AsCas12a / enAsCas12a |
|------|--------|--------|-----------------------|
| 序列长度 | 20 bp | 20 bp | 23-25 bp |
| PAM 序列 | NGG（3' 端） | NNGRRT（3' 端） | TTTV（5' 端） |

#### 通用要求
- GC 含量：40-60%
- 避免 TTTT 序列（终止转录）
- 避免同一核苷酸连续 >4 次

#### 靶向位置建议
- **Knockout**：靶向前 50% 外显子
- **Activation (CRISPRa)**：TSS 上游 -200 到 +1 bp
- **Inhibition (CRISPRi)**：TSS 上游 -50 到 +300 bp

## CRISPR 编辑结果分析

完成基因编辑实验后，可使用以下工具分析结果：

- **`analyze_cas9_mutation_outcomes`**：分析 Cas9 在靶位点诱导的突变类型和分布
- **`analyze_crispr_genome_editing`**：比较编辑前后序列，评估编辑效果

## 最佳实践

1. 始终从已验证序列开始查找
2. 每个靶基因测试 3-4 条不同 sgRNA
3. 记录所有引用和参考文献
4. 实验验证是必需的，不要完全依赖预测分数
5. 引用规范：
   - Addgene 序列：引用 PubMed ID 对应的原始论文
   - CRISPick 设计：注明 "Guide designs provided by the CRISPick web tool of the GPP at the Broad Institute"

import type { User, Conversation, Message, ExecutionStep } from '@/types';

// Mock 用户数据
export const mockUsers: Record<string, { password: string; user: User }> = {
  'admin@warphelix.com': {
    password: 'admin123',
    user: {
      id: 1,
      username: 'admin',
      email: 'admin@warphelix.com',
      role: 'super_admin',
      realName: '管理员',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=admin',
    },
  },
  'user@warphelix.com': {
    password: 'user123',
    user: {
      id: 2,
      username: 'user',
      email: 'user@warphelix.com',
      role: 'user',
      realName: '普通用户',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=user',
    },
  },
};

// Mock 对话数据
export const mockConversations: Conversation[] = [
  {
    id: 1,
    title: '蛋白质结构分析',
    status: 'active',
    messageCount: 5,
    lastMessageAt: '2025-01-20T10:30:00',
    createdAt: '2025-01-20T09:00:00',
    updatedAt: '2025-01-20T10:30:00',
  },
  {
    id: 2,
    title: '基因测序数据处理',
    status: 'completed',
    messageCount: 10,
    lastMessageAt: '2025-01-19T15:20:00',
    createdAt: '2025-01-19T14:00:00',
    updatedAt: '2025-01-19T15:20:00',
  },
  {
    id: 3,
    title: '单细胞分析流程',
    status: 'active',
    messageCount: 3,
    lastMessageAt: '2025-01-18T16:45:00',
    createdAt: '2025-01-18T16:00:00',
    updatedAt: '2025-01-18T16:45:00',
  },
];

// Mock 消息数据
export const mockMessages: Record<number, Message[]> = {
  1: [
    {
      id: 1,
      conversationId: 1,
      role: 'user',
      content: '什么是蛋白质的二级结构？',
      contentType: 'text',
      tokens: 15,
      createdAt: '2025-01-20T09:00:00',
    },
    {
      id: 2,
      conversationId: 1,
      role: 'assistant',
      content: `蛋白质的二级结构是指蛋白质多肽链中局部区域的空间排列方式，主要包括：

## 主要类型

1. **α-螺旋（Alpha Helix）**
   - 多肽链围绕中心轴呈螺旋状
   - 每3.6个氨基酸残基旋转一圈
   - 通过氢键稳定结构

2. **β-折叠（Beta Sheet）**
   - 多肽链呈锯齿状折叠
   - 可以是平行或反平行排列
   - 链间通过氢键连接

3. **β-转角（Beta Turn）**
   - 连接α-螺旋和β-折叠的转折区域
   - 通常由4个氨基酸残基组成

这些结构是蛋白质功能的基础，对理解蛋白质的生物学功能至关重要。`,
      contentType: 'markdown',
      tokens: 150,
      inputTokens: 15,
      outputTokens: 135,
      createdAt: '2025-01-20T09:00:30',
    },
    {
      id: 3,
      conversationId: 1,
      role: 'user',
      content: '如何使用 Python 分析蛋白质结构？',
      contentType: 'text',
      tokens: 20,
      createdAt: '2025-01-20T09:05:00',
    },
    {
      id: 4,
      conversationId: 1,
      role: 'assistant',
      content: `可以使用 Biopython 库来分析蛋白质结构。以下是一个示例：

\`\`\`python
from Bio.PDB import PDBParser, DSSP

# 解析 PDB 文件
parser = PDBParser()
structure = parser.get_structure('protein', '1abc.pdb')

# 使用 DSSP 分析二级结构
model = structure[0]
dssp = DSSP(model, '1abc.pdb')

# 统计二级结构
helix_count = 0
sheet_count = 0

for key in dssp:
    ss = dssp[key][2]
    if ss == 'H':  # Alpha helix
        helix_count += 1
    elif ss == 'E':  # Beta sheet
        sheet_count += 1

print(f"Alpha helices: {helix_count}")
print(f"Beta sheets: {sheet_count}")
\`\`\`

这段代码可以帮助你快速分析蛋白质的二级结构组成。`,
      contentType: 'markdown',
      tokens: 200,
      inputTokens: 20,
      outputTokens: 180,
      createdAt: '2025-01-20T09:06:00',
    },
  ],
  2: [
    {
      id: 5,
      conversationId: 2,
      role: 'user',
      content: '如何进行基因测序数据的质量控制？',
      contentType: 'text',
      tokens: 18,
      createdAt: '2025-01-19T14:00:00',
    },
    {
      id: 6,
      conversationId: 2,
      role: 'assistant',
      content: `基因测序数据的质量控制是非常重要的步骤。主要包括：

## 质量控制步骤

1. **原始数据质量评估**
   - 使用 FastQC 检查测序质量
   - 查看 Q30 比例（质量分数 ≥30 的碱基比例）
   - 检查 GC 含量分布

2. **数据过滤**
   - 去除低质量碱基
   - 去除接头序列
   - 过滤短片段

3. **比对质量检查**
   - 检查比对率
   - 查看重复率
   - 评估覆盖度

推荐使用的工具：FastQC、Trimmomatic、MultiQC 等。`,
      contentType: 'markdown',
      tokens: 180,
      inputTokens: 18,
      outputTokens: 162,
      createdAt: '2025-01-19T14:01:00',
    },
  ],
  3: [
    {
      id: 7,
      conversationId: 3,
      role: 'user',
      content: '单细胞 RNA 测序的基本流程是什么？',
      contentType: 'text',
      tokens: 16,
      createdAt: '2025-01-18T16:00:00',
    },
    {
      id: 8,
      conversationId: 3,
      role: 'assistant',
      content: `单细胞 RNA 测序（scRNA-seq）的基本流程包括：

## 实验流程

1. **样本制备**
   - 组织解离成单细胞悬液
   - 细胞分选和质量控制

2. **文库构建**
   - 单细胞捕获（10x Genomics、Drop-seq 等）
   - cDNA 合成和扩增
   - 测序文库制备

3. **测序**
   - 高通量测序（Illumina 平台）

## 数据分析流程

1. **预处理**
   - 比对到参考基因组
   - 基因表达矩阵生成

2. **质量控制**
   - 过滤低质量细胞
   - 去除双细胞

3. **下游分析**
   - 归一化
   - 降维（PCA、t-SNE、UMAP）
   - 聚类分析
   - 差异表达分析
   - 细胞类型注释

推荐使用 Seurat 或 Scanpy 进行分析。`,
      contentType: 'markdown',
      tokens: 220,
      inputTokens: 16,
      outputTokens: 204,
      createdAt: '2025-01-18T16:02:00',
    },
  ],
};

// Mock 执行步骤数据
export const mockExecutionSteps: ExecutionStep[] = [
  {
    id: 1,
    conversationId: 1,
    messageId: 2,
    stepOrder: 1,
    stepType: 'reasoning',
    stepName: '分析问题',
    status: 'success',
    durationMs: 500,
    startedAt: '2025-01-20T09:00:01',
    completedAt: '2025-01-20T09:00:01.5',
  },
  {
    id: 2,
    conversationId: 1,
    messageId: 2,
    stepOrder: 2,
    stepType: 'tool_call',
    stepName: '搜索知识库',
    toolName: 'search_knowledge',
    toolInput: {
      query: '蛋白质二级结构',
      limit: 5,
    },
    toolOutput: '找到 5 篇相关文献',
    status: 'success',
    durationMs: 1200,
    startedAt: '2025-01-20T09:00:02',
    completedAt: '2025-01-20T09:00:03.2',
  },
  {
    id: 3,
    conversationId: 1,
    messageId: 2,
    stepOrder: 3,
    stepType: 'tool_call',
    stepName: '生成回答',
    toolName: 'generate_answer',
    toolInput: {
      context: '蛋白质二级结构相关知识',
      question: '什么是蛋白质的二级结构？',
    },
    toolOutput: '生成完整回答',
    status: 'success',
    durationMs: 2000,
    startedAt: '2025-01-20T09:00:04',
    completedAt: '2025-01-20T09:00:06',
  },
];

// 生成 Mock Token
export function generateMockToken(userId: number): string {
  return `mock_token_${userId}_${Date.now()}`;
}

// 延迟函数（模拟网络请求）
export function delay(ms: number = 500): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

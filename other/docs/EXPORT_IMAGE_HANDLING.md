# 对话导出 - 图片处理说明

## 问题背景

在对话导出功能中，执行步骤可能包含图片数据（如数据可视化图表、分析结果图等）。这些图片通常以 base64 编码格式存储在数据库中。

## 解决方案：ZIP 打包

### 导出策略

1. **无图片**：直接导出 Markdown 文件（`.md`）
2. **有图片**：导出 ZIP 压缩包（`.zip`），包含：
   - Markdown 文件
   - images/ 目录（包含所有图片）

### ZIP 文件结构

```
conversation_123_1234567890.zip
├── conversation_123.md          # Markdown 文件
└── images/                       # 图片目录
    ├── image_1234567890.png
    ├── image_1234567891.jpg
    └── image_1234567892.svg
```

### Markdown 中的图片引用

```markdown
## 🤖 Assistant Message #2

### 🔧 Execution Steps

#### Step 1: generate_plot

**Output:**

![Image](images/image_1234567890.png)

The plot shows the correlation between...
```

## 实现细节

### 1. 图片提取

从执行步骤的输出中提取 base64 图片：

```java
// 匹配 base64 图片数据
Pattern base64Pattern = Pattern.compile("data:image/([^;]+);base64,([^\"\\s]+)");
Matcher matcher = base64Pattern.matcher(output);

while (matcher.find()) {
    String imageType = matcher.group(1);  // png, jpg, svg 等
    String base64Data = matcher.group(2); // base64 编码的图片数据
    
    // 解码并保存
    byte[] imageBytes = Base64.getDecoder().decode(base64Data);
    Files.write(imagePath, imageBytes);
}
```

### 2. 图片保存

图片保存到临时导出目录：

```
exports/conversations/
└── conversation_123_1234567890/
    ├── conversation_123.md
    └── images/
        └── image_1234567890.png
```

### 3. ZIP 打包

使用 Java 的 ZipOutputStream 打包：

```java
try (ZipOutputStream zos = new ZipOutputStream(
        new FileOutputStream(zipFilePath.toFile()))) {
    
    Files.walk(sourceDir)
        .filter(path -> !Files.isDirectory(path))
        .forEach(path -> {
            ZipEntry zipEntry = new ZipEntry(
                sourceDir.relativize(path).toString()
            );
            zos.putNextEntry(zipEntry);
            Files.copy(path, zos);
            zos.closeEntry();
        });
}
```

### 4. 清理临时文件

打包完成后删除临时目录：

```java
Files.walk(directory)
    .sorted(Comparator.reverseOrder())
    .forEach(path -> Files.delete(path));
```

## 用户体验

### 下载文件

- **无图片**：`conversation_123.md` (几 KB)
- **有图片**：`conversation_123_1234567890.zip` (可能几 MB)

### 查看内容

1. 解压 ZIP 文件
2. 用 Markdown 阅读器打开 `.md` 文件
3. 图片会自动显示（相对路径引用）

### 支持的 Markdown 阅读器

- **Typora**: 完美支持
- **VS Code**: 使用 Markdown Preview
- **GitHub**: 上传后可直接查看
- **Obsidian**: 完美支持
- **MacDown**: 完美支持

## 图片格式支持

### 当前支持

- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)
- SVG (`.svg`)
- GIF (`.gif`)

### 检测逻辑

```java
private boolean containsImageData(String output) {
    return output.contains("data:image/") ||  // base64 图片
           output.contains(".png") || 
           output.contains(".jpg") || 
           output.contains(".jpeg") ||
           output.contains(".svg");
}
```

## 性能考虑

### 文件大小

| 场景 | 文件大小 | 处理时间 |
|------|---------|---------|
| 纯文本对话 | < 100 KB | < 1s |
| 1-5 张图片 | 1-5 MB | 1-2s |
| 5-10 张图片 | 5-10 MB | 2-5s |
| 10+ 张图片 | > 10 MB | > 5s |

### 优化建议

1. **图片压缩**：在保存前压缩图片
2. **异步处理**：对于大文件，使用异步导出
3. **进度反馈**：显示导出进度
4. **大小限制**：限制单次导出的最大文件大小

## 错误处理

### 图片解码失败

```java
try {
    byte[] imageBytes = Base64.getDecoder().decode(base64Data);
    Files.write(imagePath, imageBytes);
} catch (Exception e) {
    log.error("保存图片失败", e);
    result.append("[Image data - failed to save]");
}
```

### ZIP 打包失败

如果 ZIP 打包失败，回退到只导出 Markdown：

```java
try {
    createZipFile(exportDir, zipFilePath);
} catch (IOException e) {
    log.error("ZIP 打包失败，回退到 MD 导出", e);
    // 返回 MD 文件
}
```

## 安全考虑

### 1. 文件大小限制

```java
private static final long MAX_IMAGE_SIZE = 10 * 1024 * 1024; // 10 MB
private static final long MAX_EXPORT_SIZE = 50 * 1024 * 1024; // 50 MB

if (imageBytes.length > MAX_IMAGE_SIZE) {
    throw new IllegalArgumentException("图片过大");
}
```

### 2. 文件类型验证

```java
private boolean isValidImageType(String imageType) {
    return Arrays.asList("png", "jpg", "jpeg", "svg", "gif")
        .contains(imageType.toLowerCase());
}
```

### 3. 路径安全

```java
// 防止路径遍历攻击
Path imagePath = exportDir.resolve("images").resolve(filename);
if (!imagePath.startsWith(exportDir)) {
    throw new SecurityException("非法路径");
}
```

## 示例场景

### 场景 1：数据分析对话

**对话内容**：
- 用户：分析这个数据集的分布
- AI：生成了 3 张图表（直方图、散点图、箱线图）

**导出结果**：
```
conversation_456.zip (2.5 MB)
├── conversation_456.md
└── images/
    ├── histogram.png (800 KB)
    ├── scatter.png (900 KB)
    └── boxplot.png (800 KB)
```

### 场景 2：纯文本对话

**对话内容**：
- 用户：解释 CRISPR 技术
- AI：纯文本回答

**导出结果**：
```
conversation_789.md (15 KB)
```

## 未来改进

### 1. 图片优化

- 自动压缩大图片
- 转换为 WebP 格式
- 生成缩略图

### 2. 多种导出格式

- PDF（包含嵌入图片）
- HTML（单文件，图片 base64 嵌入）
- DOCX（Word 文档）

### 3. 云存储集成

- 上传到 S3/OSS
- 生成分享链接
- 设置过期时间

### 4. 批量导出

- 导出多个对话到一个 ZIP
- 按日期范围导出
- 按标签/分类导出

## 相关文档

- [导出功能实现](./EXPORT_FEATURE.md)
- [快速使用指南](./EXPORT_QUICK_GUIDE.md)
- [权限说明](./EXPORT_PERMISSIONS.md)

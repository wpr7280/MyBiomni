package com.qusu.mybiomni.service;

import com.qusu.mybiomni.dao.mysql.dao.ConversationDAO;
import com.qusu.mybiomni.dao.mysql.dao.ExecutionStepDAO;
import com.qusu.mybiomni.dao.mysql.dao.MessageDAO;
import com.qusu.mybiomni.dao.mysql.model.ConversationDO;
import com.qusu.mybiomni.dao.mysql.model.ExecutionStepDO;
import com.qusu.mybiomni.dao.mysql.model.ExecutionStepDOExample;
import com.qusu.mybiomni.dao.mysql.model.MessageDO;
import com.qusu.mybiomni.dao.mysql.model.MessageDOExample;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 对话导出服务
 */
@Service
@Slf4j
public class ConversationExportService {

    @Autowired
    private ConversationDAO conversationDAO;

    @Autowired
    private MessageDAO messageDAO;

    @Autowired
    private ExecutionStepDAO executionStepDAO;

    private static final SimpleDateFormat DATE_FORMATTER = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
    private static final String EXPORT_BASE_DIR = "exports/conversations";

    /**
     * 导出对话为 Markdown 文件（打包为 ZIP）
     *
     * @param conversationId 对话ID
     * @param userId 用户ID（用于权限验证）
     * @param isAdmin 是否为管理员
     * @param includeImages 是否包含图片
     * @return 导出文件的路径（ZIP 或 MD）
     */
    public ExportResult exportConversationToMarkdown(Integer conversationId, Integer userId, boolean isAdmin, boolean includeImages) throws Exception {
        // 验证对话存在
        ConversationDO conversation = conversationDAO.selectByPrimaryKey(conversationId);
        if (conversation == null || conversation.getDeletedAt() != null) {
            throw new IllegalArgumentException("对话不存在");
        }
        
        // 权限验证：管理员可以导出任何对话，普通用户只能导出自己的对话
        if (!isAdmin && !conversation.getUserId().equals(userId)) {
            throw new IllegalArgumentException("无权限访问此对话");
        }

        // 获取所有消息
        MessageDOExample messageExample = new MessageDOExample();
        messageExample.createCriteria().andConversationIdEqualTo(conversationId);
        messageExample.setOrderByClause("created_at ASC");
        List<MessageDO> messages = messageDAO.selectByExample(messageExample);
        
        if (messages == null || messages.isEmpty()) {
            throw new IllegalArgumentException("对话没有消息内容");
        }

        // 创建临时导出目录
        String exportDirName = String.format("conversation_%d_%s", conversationId, System.currentTimeMillis());
        Path exportDir = Paths.get(EXPORT_BASE_DIR, exportDirName);
        Files.createDirectories(exportDir);

        // 用于收集图片文件
        List<String> imageFiles = new ArrayList<>();

        // 生成 Markdown 内容
        String markdownContent = generateMarkdownContent(conversation, messages, includeImages, exportDir, imageFiles);

        // 保存 Markdown 文件
        String mdFilename = String.format("conversation_%d.md", conversationId);
        Path mdFilePath = exportDir.resolve(mdFilename);
        try (FileWriter writer = new FileWriter(mdFilePath.toFile())) {
            writer.write(markdownContent);
        }

        // 如果有图片，打包成 ZIP；否则直接返回 MD 文件
        if (includeImages && !imageFiles.isEmpty()) {
            String zipFilename = exportDirName + ".zip";
            Path zipFilePath = Paths.get(EXPORT_BASE_DIR, zipFilename);
            createZipFile(exportDir, zipFilePath);
            
            // 删除临时目录
            deleteDirectory(exportDir);
            
            log.info("对话导出成功（ZIP）: conversationId={}, filepath={}, images={}", 
                conversationId, zipFilePath, imageFiles.size());
            return new ExportResult(zipFilePath.toString(), true, imageFiles.size());
        } else {
            // 只有 Markdown，移动到根目录
            Path finalMdPath = Paths.get(EXPORT_BASE_DIR, mdFilename);
            Files.move(mdFilePath, finalMdPath, java.nio.file.StandardCopyOption.REPLACE_EXISTING);
            
            // 删除临时目录
            deleteDirectory(exportDir);
            
            log.info("对话导出成功（MD）: conversationId={}, filepath={}", conversationId, finalMdPath);
            return new ExportResult(finalMdPath.toString(), false, 0);
        }
    }

    /**
     * 导出结果
     */
    public static class ExportResult {
        private final String filepath;
        private final boolean isZip;
        private final int imageCount;

        public ExportResult(String filepath, boolean isZip, int imageCount) {
            this.filepath = filepath;
            this.isZip = isZip;
            this.imageCount = imageCount;
        }

        public String getFilepath() { return filepath; }
        public boolean isZip() { return isZip; }
        public int getImageCount() { return imageCount; }
    }

    /**
     * 生成 Markdown 内容
     */
    private String generateMarkdownContent(ConversationDO conversation, List<MessageDO> messages, 
                                          boolean includeImages, Path exportDir, List<String> imageFiles) {
        StringBuilder md = new StringBuilder();

        // 标题和元数据
        md.append("# ").append(conversation.getTitle()).append("\n\n");
        md.append("---\n\n");
        md.append("**Conversation ID:** ").append(conversation.getId()).append("\n\n");
        md.append("**Created:** ").append(DATE_FORMATTER.format(conversation.getCreatedAt())).append("\n\n");
        md.append("**Status:** ").append(conversation.getStatus()).append("\n\n");
        md.append("**Total Messages:** ").append(conversation.getMessageCount()).append("\n\n");
        md.append("**Total Tokens:** ").append(conversation.getTotalTokens()).append("\n\n");
        md.append("---\n\n");

        // 遍历消息
        for (int i = 0; i < messages.size(); i++) {
            MessageDO message = messages.get(i);
            appendMessageToMarkdown(md, message, i + 1, includeImages, exportDir, imageFiles);
        }

        // 页脚
        md.append("\n---\n\n");
        md.append("*Exported from Biomni - ").append(DATE_FORMATTER.format(new java.util.Date())).append("*\n");

        return md.toString();
    }

    /**
     * 添加单条消息到 Markdown
     */
    private void appendMessageToMarkdown(StringBuilder md, MessageDO message, int index, 
                                        boolean includeImages, Path exportDir, List<String> imageFiles) {
        // 消息标题
        String roleIcon = message.getRole().equals("user") ? "👤" : "🤖";
        String roleLabel = message.getRole().equals("user") ? "User" : "Assistant";
        
        md.append("## ").append(roleIcon).append(" ").append(roleLabel)
          .append(" Message #").append(index).append("\n\n");
        
        md.append("**Time:** ").append(DATE_FORMATTER.format(message.getCreatedAt())).append("\n\n");
        
        if (message.getTokens() != null && message.getTokens() > 0) {
            md.append("**Tokens:** ").append(message.getTokens());
            if (message.getInputTokens() != null && message.getOutputTokens() != null) {
                md.append(" (Input: ").append(message.getInputTokens())
                  .append(", Output: ").append(message.getOutputTokens()).append(")");
            }
            md.append("\n\n");
        }

        // 消息内容
        md.append("### Content\n\n");
        md.append(message.getContent()).append("\n\n");

        // 如果是 assistant 消息，添加执行步骤
        if (message.getRole().equals("assistant")) {
            ExecutionStepDOExample stepExample = new ExecutionStepDOExample();
            stepExample.createCriteria().andMessageIdEqualTo(message.getId());
            stepExample.setOrderByClause("step_order ASC");
            List<ExecutionStepDO> steps = executionStepDAO.selectByExample(stepExample);
            
            if (steps != null && !steps.isEmpty()) {
                appendExecutionSteps(md, steps, includeImages, exportDir, imageFiles);
            }
        }

        md.append("---\n\n");
    }

    /**
     * 添加执行步骤到 Markdown
     */
    private void appendExecutionSteps(StringBuilder md, List<ExecutionStepDO> steps, 
                                     boolean includeImages, Path exportDir, List<String> imageFiles) {
        md.append("### 🔧 Execution Steps\n\n");

        for (ExecutionStepDO step : steps) {
            md.append("#### Step ").append(step.getStepOrder()).append(": ");
            
            if (step.getStepName() != null) {
                md.append(step.getStepName());
            } else if (step.getToolName() != null) {
                md.append(step.getToolName());
            } else {
                md.append(step.getStepType());
            }
            md.append("\n\n");

            // 状态标记
            String statusEmoji = getStatusEmoji(step.getStatus());
            md.append("**Status:** ").append(statusEmoji).append(" ").append(step.getStatus()).append("\n\n");

            // 工具调用信息
            if (step.getToolName() != null) {
                md.append("**Tool:** `").append(step.getToolName()).append("`\n\n");
            }

            // 工具输入
            if (step.getToolInput() != null && !step.getToolInput().isEmpty()) {
                md.append("**Input:**\n\n");
                md.append("```json\n");
                md.append(formatJson(step.getToolInput()));
                md.append("\n```\n\n");
            }

            // 工具输出
            if (step.getToolOutput() != null && !step.getToolOutput().isEmpty()) {
                md.append("**Output:**\n\n");
                
                // 检查是否包含图片
                if (includeImages && containsImageData(step.getToolOutput())) {
                    md.append(processImagesInOutput(step.getToolOutput(), exportDir, imageFiles));
                } else {
                    md.append("```\n");
                    md.append(step.getToolOutput());
                    md.append("\n```\n\n");
                }
            }

            // 错误信息
            if (step.getErrorMessage() != null && !step.getErrorMessage().isEmpty()) {
                md.append("**Error:**\n\n");
                md.append("```\n");
                md.append(step.getErrorMessage());
                md.append("\n```\n\n");
            }

            // 执行时长
            if (step.getDurationMs() != null && step.getDurationMs() > 0) {
                md.append("**Duration:** ").append(step.getDurationMs()).append(" ms\n\n");
            }

            md.append("\n");
        }
    }

    /**
     * 获取状态对应的 emoji
     */
    private String getStatusEmoji(String status) {
        switch (status.toLowerCase()) {
            case "success":
                return "✅";
            case "failed":
                return "❌";
            case "running":
                return "⏳";
            default:
                return "⚪";
        }
    }

    /**
     * 格式化 JSON 字符串
     */
    private String formatJson(String json) {
        try {
            // 简单的 JSON 格式化，可以使用 Jackson 或 Gson 进行更好的格式化
            return json.replace(",", ",\n  ").replace("{", "{\n  ").replace("}", "\n}");
        } catch (Exception e) {
            return json;
        }
    }

    /**
     * 检查输出是否包含图片数据
     */
    private boolean containsImageData(String output) {
        // 检查是否包含 base64 图片数据或图片路径
        return output.contains("data:image/") || 
               output.contains(".png") || 
               output.contains(".jpg") || 
               output.contains(".jpeg") ||
               output.contains(".svg");
    }

    /**
     * 处理输出中的图片
     */
    private String processImagesInOutput(String output, Path exportDir, List<String> imageFiles) {
        StringBuilder result = new StringBuilder();
        
        // 匹配 base64 图片数据
        Pattern base64Pattern = Pattern.compile("data:image/([^;]+);base64,([^\"\\s]+)");
        Matcher matcher = base64Pattern.matcher(output);
        
        int lastEnd = 0;
        while (matcher.find()) {
            result.append(output, lastEnd, matcher.start());
            
            String imageType = matcher.group(1);
            String base64Data = matcher.group(2);
            
            // 保存图片并返回引用
            try {
                String imagePath = saveBase64Image(base64Data, imageType, exportDir);
                imageFiles.add(imagePath);
                result.append("![Image](").append(imagePath).append(")");
            } catch (Exception e) {
                log.error("保存图片失败", e);
                result.append("[Image data - failed to save]");
            }
            
            lastEnd = matcher.end();
        }
        result.append(output.substring(lastEnd));
        
        return result.toString();
    }

    /**
     * 保存 base64 图片到导出目录
     */
    private String saveBase64Image(String base64Data, String imageType, Path exportDir) throws IOException {
        byte[] imageBytes = Base64.getDecoder().decode(base64Data);
        
        // 创建 images 子目录
        Path imagesDir = exportDir.resolve("images");
        Files.createDirectories(imagesDir);
        
        String filename = String.format("image_%s.%s", System.currentTimeMillis(), imageType);
        Path imagePath = imagesDir.resolve(filename);
        
        Files.write(imagePath, imageBytes);
        
        // 返回相对路径（相对于 Markdown 文件）
        return "images/" + filename;
    }

    /**
     * 创建 ZIP 文件
     */
    private void createZipFile(Path sourceDir, Path zipFilePath) throws IOException {
        try (java.util.zip.ZipOutputStream zos = new java.util.zip.ZipOutputStream(
                new java.io.FileOutputStream(zipFilePath.toFile()))) {
            
            Files.walk(sourceDir)
                .filter(path -> !Files.isDirectory(path))
                .forEach(path -> {
                    java.util.zip.ZipEntry zipEntry = new java.util.zip.ZipEntry(
                        sourceDir.relativize(path).toString()
                    );
                    try {
                        zos.putNextEntry(zipEntry);
                        Files.copy(path, zos);
                        zos.closeEntry();
                    } catch (IOException e) {
                        log.error("添加文件到 ZIP 失败: {}", path, e);
                    }
                });
        }
    }

    /**
     * 递归删除目录
     */
    private void deleteDirectory(Path directory) throws IOException {
        if (Files.exists(directory)) {
            Files.walk(directory)
                .sorted(java.util.Comparator.reverseOrder())
                .forEach(path -> {
                    try {
                        Files.delete(path);
                    } catch (IOException e) {
                        log.error("删除文件失败: {}", path, e);
                    }
                });
        }
    }

    /**
     * 获取导出文件
     */
    public File getExportFile(String filepath) {
        File file = new File(filepath);
        if (!file.exists() || !file.isFile()) {
            throw new IllegalArgumentException("文件不存在");
        }
        return file;
    }

    /**
     * 清理过期的导出文件（可选，定期清理）
     */
    public void cleanupOldExports(int daysOld) {
        try {
            Path exportDir = Paths.get(EXPORT_BASE_DIR);
            if (!Files.exists(exportDir)) {
                return;
            }

            long cutoffTime = System.currentTimeMillis() - (daysOld * 24L * 60 * 60 * 1000);
            
            Files.walk(exportDir)
                .filter(Files::isRegularFile)
                .filter(path -> {
                    try {
                        return Files.getLastModifiedTime(path).toMillis() < cutoffTime;
                    } catch (IOException e) {
                        return false;
                    }
                })
                .forEach(path -> {
                    try {
                        Files.delete(path);
                        log.info("删除过期导出文件: {}", path);
                    } catch (IOException e) {
                        log.error("删除文件失败: {}", path, e);
                    }
                });
        } catch (IOException e) {
            log.error("清理导出文件失败", e);
        }
    }
}

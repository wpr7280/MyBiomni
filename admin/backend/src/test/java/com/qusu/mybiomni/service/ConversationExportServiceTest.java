package com.qusu.mybiomni.service;

import com.qusu.mybiomni.dao.mysql.dao.ConversationDAO;
import com.qusu.mybiomni.dao.mysql.dao.ExecutionStepDAO;
import com.qusu.mybiomni.dao.mysql.dao.MessageDAO;
import com.qusu.mybiomni.dao.mysql.model.ConversationDO;
import com.qusu.mybiomni.dao.mysql.model.ExecutionStepDO;
import com.qusu.mybiomni.dao.mysql.model.MessageDO;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.io.File;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

/**
 * ConversationExportService 单元测试
 */
class ConversationExportServiceTest {

    @Mock
    private ConversationDAO conversationDAO;

    @Mock
    private MessageDAO messageDAO;

    @Mock
    private ExecutionStepDAO executionStepDAO;

    @InjectMocks
    private ConversationExportService exportService;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void testExportConversationToMarkdown_Success() throws Exception {
        // 准备测试数据
        Integer conversationId = 1;
        Integer userId = 1;

        ConversationDO conversation = new ConversationDO();
        conversation.setId(conversationId);
        conversation.setUserId(userId);
        conversation.setTitle("Test Conversation");
        conversation.setStatus("active");
        conversation.setMessageCount(2);
        conversation.setTotalTokens(500);
        conversation.setCreatedAt(new Date());

        List<MessageDO> messages = new ArrayList<>();
        
        MessageDO userMessage = new MessageDO();
        userMessage.setId(1);
        userMessage.setConversationId(conversationId);
        userMessage.setRole("user");
        userMessage.setContent("Test question");
        userMessage.setTokens(50);
        userMessage.setCreatedAt(new Date());
        messages.add(userMessage);

        MessageDO assistantMessage = new MessageDO();
        assistantMessage.setId(2);
        assistantMessage.setConversationId(conversationId);
        assistantMessage.setRole("assistant");
        assistantMessage.setContent("Test answer");
        assistantMessage.setTokens(450);
        assistantMessage.setInputTokens(50);
        assistantMessage.setOutputTokens(400);
        assistantMessage.setCreatedAt(new Date());
        messages.add(assistantMessage);

        // Mock DAO 调用
        when(conversationDAO.selectByPrimaryKey(conversationId)).thenReturn(conversation);
        when(messageDAO.selectByExample(any())).thenReturn(messages);
        when(executionStepDAO.selectByExample(any())).thenReturn(new ArrayList<>());

        // 执行导出（普通用户导出自己的对话）
        ConversationExportService.ExportResult result = exportService.exportConversationToMarkdown(
            conversationId, userId, false, true
        );

        // 验证结果
        assertNotNull(result);
        assertNotNull(result.getFilepath());
        assertTrue(result.getFilepath().contains("conversation_1"));

        // 验证文件存在
        File file = new File(result.getFilepath());
        assertTrue(file.exists());

        // 清理测试文件
        file.delete();
    }

    @Test
    void testExportConversationToMarkdown_AdminCanExportAnyConversation() throws Exception {
        // 准备测试数据 - 管理员导出其他用户的对话
        Integer conversationId = 1;
        Integer conversationOwnerId = 2;  // 对话所有者
        Integer adminUserId = 1;          // 管理员

        ConversationDO conversation = new ConversationDO();
        conversation.setId(conversationId);
        conversation.setUserId(conversationOwnerId);  // 对话属于用户2
        conversation.setTitle("User 2's Conversation");
        conversation.setStatus("active");
        conversation.setMessageCount(1);
        conversation.setTotalTokens(100);
        conversation.setCreatedAt(new Date());

        List<MessageDO> messages = new ArrayList<>();
        MessageDO message = new MessageDO();
        message.setId(1);
        message.setConversationId(conversationId);
        message.setRole("user");
        message.setContent("Test");
        message.setTokens(100);
        message.setCreatedAt(new Date());
        messages.add(message);

        // Mock DAO 调用
        when(conversationDAO.selectByPrimaryKey(conversationId)).thenReturn(conversation);
        when(messageDAO.selectByExample(any())).thenReturn(messages);
        when(executionStepDAO.selectByExample(any())).thenReturn(new ArrayList<>());

        // 执行导出（管理员导出其他用户的对话）
        ConversationExportService.ExportResult result = exportService.exportConversationToMarkdown(
            conversationId, 
            adminUserId, 
            true,  // isAdmin = true
            true
        );

        // 验证结果 - 管理员应该可以成功导出
        assertNotNull(result);
        assertNotNull(result.getFilepath());
        assertTrue(result.getFilepath().contains("conversation_1"));

        // 清理测试文件
        new File(result.getFilepath()).delete();
    }

    @Test
    void testExportConversationToMarkdown_UnauthorizedAccess() {
        // 准备测试数据 - 普通用户尝试导出其他用户的对话
        Integer conversationId = 1;
        Integer conversationOwnerId = 1;
        Integer unauthorizedUserId = 2;  // 不同的用户

        ConversationDO conversation = new ConversationDO();
        conversation.setId(conversationId);
        conversation.setUserId(conversationOwnerId);

        // Mock DAO 调用
        when(conversationDAO.selectByPrimaryKey(conversationId)).thenReturn(conversation);

        // 执行并验证异常（普通用户尝试导出其他用户的对话）
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            exportService.exportConversationToMarkdown(
                conversationId, 
                unauthorizedUserId, 
                false,  // isAdmin = false
                true
            );
        });

        assertEquals("无权限访问此对话", exception.getMessage());
    }

    @Test
    void testExportConversationToMarkdown_ConversationNotFound() {
        // Mock DAO 返回 null
        when(conversationDAO.selectByPrimaryKey(any())).thenReturn(null);

        // 执行并验证异常
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            exportService.exportConversationToMarkdown(1, 1, false, true);
        });

        assertEquals("对话不存在", exception.getMessage());
    }

    @Test
    void testExportConversationToMarkdown_NoMessages() {
        // 准备测试数据
        Integer conversationId = 1;
        Integer userId = 1;

        ConversationDO conversation = new ConversationDO();
        conversation.setId(conversationId);
        conversation.setUserId(userId);

        // Mock DAO 调用
        when(conversationDAO.selectByPrimaryKey(conversationId)).thenReturn(conversation);
        when(messageDAO.selectByExample(any())).thenReturn(new ArrayList<>());

        // 执行并验证异常
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            exportService.exportConversationToMarkdown(conversationId, userId, false, true);
        });

        assertEquals("对话没有消息内容", exception.getMessage());
    }

    @Test
    void testGetExportFile_FileExists() {
        // 创建临时测试文件
        String testFilePath = "exports/conversations/test_file.md";
        File testFile = new File(testFilePath);
        
        try {
            testFile.getParentFile().mkdirs();
            testFile.createNewFile();

            // 执行测试
            File result = exportService.getExportFile(testFilePath);

            // 验证结果
            assertNotNull(result);
            assertTrue(result.exists());
            assertEquals(testFile.getAbsolutePath(), result.getAbsolutePath());

        } catch (Exception e) {
            fail("Test setup failed: " + e.getMessage());
        } finally {
            // 清理测试文件
            testFile.delete();
        }
    }

    @Test
    void testGetExportFile_FileNotExists() {
        String nonExistentPath = "exports/conversations/non_existent.md";

        // 执行并验证异常
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            exportService.getExportFile(nonExistentPath);
        });

        assertEquals("文件不存在", exception.getMessage());
    }
}

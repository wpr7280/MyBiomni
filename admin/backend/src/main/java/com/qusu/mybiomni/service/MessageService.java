package com.qusu.mybiomni.service;

import com.qusu.mybiomni.common.request.PageRequest;
import com.qusu.mybiomni.controller.message.response.MessageVO;
import com.qusu.mybiomni.dao.mysql.dao.ConversationDAO;
import com.qusu.mybiomni.dao.mysql.dao.MessageDAO;
import com.qusu.mybiomni.dao.mysql.model.ConversationDO;
import com.qusu.mybiomni.dao.mysql.model.MessageDO;
import com.qusu.mybiomni.dao.mysql.model.MessageDOExample;
import org.apache.ibatis.session.RowBounds;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class MessageService {

    @Autowired
    private MessageDAO messageDAO;
    
    @Autowired
    private ConversationDAO conversationDAO;

    /**
     * 获取消息列表
     */
    public List<MessageVO> getMessageList(Integer conversationId, Integer userId, PageRequest pageRequest) {
        // 验证对话权限
        checkConversationAccess(conversationId, userId);
        
        MessageDOExample example = new MessageDOExample();
        example.createCriteria()
                .andConversationIdEqualTo(conversationId);
        example.setOrderByClause("created_at ASC");
        
        // 分页
        RowBounds rowBounds = new RowBounds(pageRequest.getStart(), pageRequest.getPageSize());
        
        List<MessageDO> messages = messageDAO.selectByExampleWithRowbounds(example,rowBounds);
        
        return messages.stream()
                .map(this::convertToVO)
                .collect(Collectors.toList());
    }

    /**
     * 获取消息总数
     */
    public long getMessageCount(Integer conversationId) {
        MessageDOExample example = new MessageDOExample();
        example.createCriteria()
                .andConversationIdEqualTo(conversationId);
        
        return messageDAO.countByExample(example);
    }

    /**
     * 发送消息
     */
    @Transactional
    public MessageVO sendMessage(Integer conversationId, Integer userId, String content) {
        // 验证对话权限
        ConversationDO conversation = checkConversationAccess(conversationId, userId);
        
        // TODO: 检查配额
        
        // 创建用户消息
        MessageDO message = new MessageDO();
        message.setConversationId(conversationId);
        message.setRole("user");
        message.setContent(content);
        message.setContentType("text");
        message.setTokens(estimateTokens(content));
        message.setInputTokens(estimateTokens(content));
        message.setOutputTokens(0);
        message.setCreatedAt(new Date());
        
        messageDAO.insert(message);
        
        // 更新对话统计
        conversation.setMessageCount(conversation.getMessageCount() + 1);
        conversation.setLastMessageAt(new Date());
        conversation.setUpdatedAt(new Date());
        conversationDAO.updateByPrimaryKey(conversation);
        
        return convertToVO(message);
    }

    /**
     * 验证对话访问权限
     */
    private ConversationDO checkConversationAccess(Integer conversationId, Integer userId) {
        ConversationDO conversation = conversationDAO.selectByPrimaryKey(conversationId);
        
        if (conversation == null || conversation.getDeletedAt() != null) {
            throw new RuntimeException("Conversation not found");
        }
        
        if (!conversation.getUserId().equals(userId)) {
            throw new RuntimeException("Access denied for this conversation");
        }
        
        return conversation;
    }

    /**
     * 估算 Token 数量（简单实现：字符数 / 4）
     */
    private Integer estimateTokens(String content) {
        return Math.max(1, content.length() / 4);
    }

    /**
     * 转换为 VO
     */
    private MessageVO convertToVO(MessageDO message) {
        MessageVO vo = new MessageVO();
        BeanUtils.copyProperties(message, vo);
        return vo;
    }
}

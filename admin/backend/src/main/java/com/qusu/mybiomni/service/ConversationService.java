package com.qusu.mybiomni.service;

import com.qusu.mybiomni.common.request.PageRequest;
import com.qusu.mybiomni.controller.conversation.response.ConversationVO;
import com.qusu.mybiomni.dao.mysql.dao.ConversationDAO;
import com.qusu.mybiomni.dao.mysql.model.ConversationDO;
import com.qusu.mybiomni.dao.mysql.model.ConversationDOExample;
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
public class ConversationService {

    @Autowired
    private ConversationDAO conversationDAO;

    /**
     * 获取对话列表
     */
    public List<ConversationVO> getConversationList(Integer userId, PageRequest pageRequest) {
        ConversationDOExample example = new ConversationDOExample();
        example.createCriteria()
                .andUserIdEqualTo(userId)
                .andDeletedAtIsNull();
        example.setOrderByClause("updated_at DESC");

        // 分页
        RowBounds rowBounds = new RowBounds(pageRequest.getStart(), pageRequest.getPageSize());
        List<ConversationDO> conversations = conversationDAO.selectByExampleWithRowbounds(example, rowBounds);

        return conversations.stream()
                .map(this::convertToVO)
                .collect(Collectors.toList());
    }

    /**
     * 获取对话总数
     */
    public long getConversationCount(Integer userId) {
        ConversationDOExample example = new ConversationDOExample();
        example.createCriteria()
                .andUserIdEqualTo(userId)
                .andDeletedAtIsNull();

        return conversationDAO.countByExample(example);
    }

    /**
     * 创建新对话
     */
    @Transactional
    public ConversationVO createConversation(Integer userId, String title) {
        ConversationDO conversation = new ConversationDO();
        conversation.setUserId(userId);
        conversation.setTitle(title != null && !title.trim().isEmpty() ? title : "新对话");
        conversation.setStatus("active");
        conversation.setMessageCount(0);
        conversation.setTotalTokens(0);
        conversation.setTotalDurationMs(0);
        conversation.setCreatedAt(new Date());
        conversation.setUpdatedAt(new Date());

        conversationDAO.insert(conversation);

        return convertToVO(conversation);
    }

    /**
     * 获取对话详情
     */
    public ConversationVO getConversation(Integer id, Integer userId) {
        ConversationDO conversation = conversationDAO.selectByPrimaryKey(id);

        if (conversation == null || conversation.getDeletedAt() != null) {
            throw new RuntimeException("对话不存在");
        }

        if (!conversation.getUserId().equals(userId)) {
            throw new RuntimeException("无权访问此对话");
        }

        return convertToVO(conversation);
    }

    /**
     * 更新对话标题
     */
    @Transactional
    public void updateConversation(Integer id, Integer userId, String title) {
        ConversationDO conversation = conversationDAO.selectByPrimaryKey(id);

        if (conversation == null || conversation.getDeletedAt() != null) {
            throw new RuntimeException("对话不存在");
        }

        if (!conversation.getUserId().equals(userId)) {
            throw new RuntimeException("无权访问此对话");
        }

        conversation.setTitle(title);
        conversation.setUpdatedAt(new Date());

        conversationDAO.updateByPrimaryKey(conversation);
    }

    /**
     * 删除对话（软删除）
     */
    @Transactional
    public void deleteConversation(Integer id, Integer userId) {
        ConversationDO conversation = conversationDAO.selectByPrimaryKey(id);

        if (conversation == null || conversation.getDeletedAt() != null) {
            throw new RuntimeException("对话不存在");
        }

        if (!conversation.getUserId().equals(userId)) {
            throw new RuntimeException("无权访问此对话");
        }
        conversation.setDeletedAt(new Date());
        conversationDAO.updateByPrimaryKey(conversation);
    }

    /**
     * 转换为 VO
     */
    private ConversationVO convertToVO(ConversationDO conversation) {
        ConversationVO vo = new ConversationVO();
        BeanUtils.copyProperties(conversation, vo);
        return vo;
    }
}

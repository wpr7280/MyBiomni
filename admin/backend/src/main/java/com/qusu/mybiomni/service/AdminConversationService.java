package com.qusu.mybiomni.service;

import com.qusu.mybiomni.controller.admin.request.AdminConversationListRequest;
import com.qusu.mybiomni.controller.admin.response.AdminConversationVO;
import com.qusu.mybiomni.controller.admin.response.ConversationDetailVO;
import com.qusu.mybiomni.dao.mysql.dao.AdminDAO;
import com.qusu.mybiomni.dao.mysql.dao.ConversationDAO;
import com.qusu.mybiomni.dao.mysql.dao.MessageDAO;
import com.qusu.mybiomni.dao.mysql.model.AdminDO;
import com.qusu.mybiomni.dao.mysql.model.ConversationDO;
import com.qusu.mybiomni.dao.mysql.model.ConversationDOExample;
import com.qusu.mybiomni.dao.mysql.model.MessageDO;
import com.qusu.mybiomni.dao.mysql.model.MessageDOExample;
import org.apache.ibatis.session.RowBounds;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 管理员对话管理服务
 */
@Service
public class AdminConversationService {
    
    @Autowired
    private ConversationDAO conversationDAO;
    
    @Autowired
    private AdminDAO adminDAO;
    
    @Autowired
    private MessageDAO messageDAO;
    
    /**
     * 获取对话列表（管理员视图）
     */
    public List<AdminConversationVO> getConversationList(AdminConversationListRequest request) {
        ConversationDOExample example = new ConversationDOExample();
        ConversationDOExample.Criteria criteria = example.createCriteria();
        
        // Admin can see all conversations including soft-deleted ones
        // Only filter deleted if explicitly requested
        if (request.getStatus() != null && "deleted".equals(request.getStatus().trim())) {
            criteria.andDeletedAtIsNotNull();
        } else if (request.getStatus() == null || request.getStatus().trim().isEmpty()) {
            // Show all (no deleted_at filter)
        } else {
            // Other status filters: only show non-deleted
            criteria.andDeletedAtIsNull();
            criteria.andStatusEqualTo(request.getStatus());
        }
        
        // 用户ID筛选
        if (request.getUserId() != null) {
            criteria.andUserIdEqualTo(request.getUserId());
        }
        
        // 关键词搜索（对话标题）
        if (request.getKeyword() != null && !request.getKeyword().trim().isEmpty()) {
            criteria.andTitleLike("%" + request.getKeyword().trim() + "%");
        }
        
        // 时间范围筛选
        if (request.getStartDate() != null && !request.getStartDate().trim().isEmpty()) {
            try {
                SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
                Date startDate = sdf.parse(request.getStartDate());
                criteria.andCreatedAtGreaterThanOrEqualTo(startDate);
            } catch (ParseException e) {
                // 忽略解析错误
            }
        }
        
        if (request.getEndDate() != null && !request.getEndDate().trim().isEmpty()) {
            try {
                SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
                Date endDate = sdf.parse(request.getEndDate());
                // 设置为当天的23:59:59
                endDate = new Date(endDate.getTime() + 24 * 60 * 60 * 1000 - 1);
                criteria.andCreatedAtLessThanOrEqualTo(endDate);
            } catch (ParseException e) {
                // 忽略解析错误
            }
        }
        
        // 排序：最新的在前
        example.setOrderByClause("created_at DESC");
        
        // 分页查询
        RowBounds rowBounds = new RowBounds(request.getStart(), request.getPageSize());
        List<ConversationDO> conversations = conversationDAO.selectByExampleWithRowbounds(example, rowBounds);
        
        // 转换为 VO
        return conversations.stream()
                .map(this::convertToAdminVO)
                .collect(Collectors.toList());
    }
    
    /**
     * 获取对话总数
     */
    public long getConversationCount(AdminConversationListRequest request) {
        ConversationDOExample example = new ConversationDOExample();
        ConversationDOExample.Criteria criteria = example.createCriteria();
        
        // Match the same logic as getConversationList
        if (request.getStatus() != null && "deleted".equals(request.getStatus().trim())) {
            criteria.andDeletedAtIsNotNull();
        } else if (request.getStatus() != null && !request.getStatus().trim().isEmpty()) {
            criteria.andDeletedAtIsNull();
            criteria.andStatusEqualTo(request.getStatus());
        }
        
        if (request.getUserId() != null) {
            criteria.andUserIdEqualTo(request.getUserId());
        }
        
        if (request.getKeyword() != null && !request.getKeyword().trim().isEmpty()) {
            criteria.andTitleLike("%" + request.getKeyword().trim() + "%");
        }
        
        if (request.getStartDate() != null && !request.getStartDate().trim().isEmpty()) {
            try {
                SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
                Date startDate = sdf.parse(request.getStartDate());
                criteria.andCreatedAtGreaterThanOrEqualTo(startDate);
            } catch (ParseException e) {
                // 忽略
            }
        }
        
        if (request.getEndDate() != null && !request.getEndDate().trim().isEmpty()) {
            try {
                SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
                Date endDate = sdf.parse(request.getEndDate());
                endDate = new Date(endDate.getTime() + 24 * 60 * 60 * 1000 - 1);
                criteria.andCreatedAtLessThanOrEqualTo(endDate);
            } catch (ParseException e) {
                // 忽略
            }
        }
        
        return conversationDAO.countByExample(example);
    }
    
    /**
     * 删除对话（管理员操作）
     */
    @Transactional
    public void deleteConversation(Integer conversationId) {
        ConversationDO conversation = conversationDAO.selectByPrimaryKey(conversationId);
        if (conversation == null) {
            throw new RuntimeException("Conversation not found");
        }
        
        // 软删除
        ConversationDO updateConversation = new ConversationDO();
        updateConversation.setId(conversationId);
        updateConversation.setDeletedAt(new Date());
        updateConversation.setUpdatedAt(new Date());
        conversationDAO.updateByPrimaryKeySelective(updateConversation);
    }
    
    /**
     * 获取对话详情（包含消息列表）
     */
    public ConversationDetailVO getConversationDetail(Integer conversationId) {
        // 获取对话基本信息
        ConversationDO conversation = conversationDAO.selectByPrimaryKey(conversationId);
        if (conversation == null) {
            throw new RuntimeException("Conversation not found");
        }
        
        // 转换为详情 VO
        ConversationDetailVO detail = new ConversationDetailVO();
        BeanUtils.copyProperties(conversation, detail);
        
        // 获取用户信息
        AdminDO user = adminDAO.selectByPrimaryKey(conversation.getUserId());
        if (user != null) {
            detail.setUserEmail(user.getEmail());
            detail.setUsername(user.getUsername());
        }
        
        // 获取消息列表
        MessageDOExample messageExample = new MessageDOExample();
        messageExample.createCriteria()
                .andConversationIdEqualTo(conversationId);
        messageExample.setOrderByClause("created_at ASC");
        
        List<MessageDO> messages = messageDAO.selectByExample(messageExample);
        
        // 转换消息为 VO
        List<ConversationDetailVO.MessageVO> messageVOs = messages.stream()
                .map(this::convertToMessageVO)
                .collect(Collectors.toList());
        
        detail.setMessages(messageVOs);
        
        return detail;
    }
    
    /**
     * 转换为管理员 VO
     */
    private AdminConversationVO convertToAdminVO(ConversationDO conversation) {
        AdminConversationVO vo = new AdminConversationVO();
        BeanUtils.copyProperties(conversation, vo);
        vo.setDeleted(conversation.getDeletedAt() != null);
        
        // 获取用户信息
        AdminDO user = adminDAO.selectByPrimaryKey(conversation.getUserId());
        if (user != null) {
            vo.setUserEmail(user.getEmail());
            vo.setUsername(user.getUsername());
        }
        
        return vo;
    }
    
    /**
     * 转换消息为 VO
     */
    private ConversationDetailVO.MessageVO convertToMessageVO(MessageDO message) {
        ConversationDetailVO.MessageVO vo = new ConversationDetailVO.MessageVO();
        BeanUtils.copyProperties(message, vo);
        return vo;
    }
}

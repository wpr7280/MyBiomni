package com.qusu.mybiomni.service;

import com.qusu.mybiomni.controller.admin.request.AdminConversationListRequest;
import com.qusu.mybiomni.controller.admin.response.AdminConversationVO;
import com.qusu.mybiomni.dao.mysql.dao.AdminDAO;
import com.qusu.mybiomni.dao.mysql.dao.ConversationDAO;
import com.qusu.mybiomni.dao.mysql.model.AdminDO;
import com.qusu.mybiomni.dao.mysql.model.ConversationDO;
import com.qusu.mybiomni.dao.mysql.model.ConversationDOExample;
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
    
    /**
     * 获取对话列表（管理员视图）
     */
    public List<AdminConversationVO> getConversationList(AdminConversationListRequest request) {
        ConversationDOExample example = new ConversationDOExample();
        ConversationDOExample.Criteria criteria = example.createCriteria();
        
        // 软删除过滤
        criteria.andDeletedAtIsNull();
        
        // 用户ID筛选
        if (request.getUserId() != null) {
            criteria.andUserIdEqualTo(request.getUserId());
        }
        
        // 关键词搜索（对话标题）
        if (request.getKeyword() != null && !request.getKeyword().trim().isEmpty()) {
            criteria.andTitleLike("%" + request.getKeyword().trim() + "%");
        }
        
        // 状态筛选
        if (request.getStatus() != null && !request.getStatus().trim().isEmpty()) {
            criteria.andStatusEqualTo(request.getStatus());
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
        
        criteria.andDeletedAtIsNull();
        
        if (request.getUserId() != null) {
            criteria.andUserIdEqualTo(request.getUserId());
        }
        
        if (request.getKeyword() != null && !request.getKeyword().trim().isEmpty()) {
            criteria.andTitleLike("%" + request.getKeyword().trim() + "%");
        }
        
        if (request.getStatus() != null && !request.getStatus().trim().isEmpty()) {
            criteria.andStatusEqualTo(request.getStatus());
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
            throw new RuntimeException("对话不存在");
        }
        
        // 软删除
        ConversationDO updateConversation = new ConversationDO();
        updateConversation.setId(conversationId);
        updateConversation.setDeletedAt(new Date());
        updateConversation.setUpdatedAt(new Date());
        conversationDAO.updateByPrimaryKeySelective(updateConversation);
    }
    
    /**
     * 转换为管理员 VO
     */
    private AdminConversationVO convertToAdminVO(ConversationDO conversation) {
        AdminConversationVO vo = new AdminConversationVO();
        BeanUtils.copyProperties(conversation, vo);
        
        // 获取用户信息
        AdminDO user = adminDAO.selectByPrimaryKey(conversation.getUserId());
        if (user != null) {
            vo.setUserEmail(user.getEmail());
            vo.setUsername(user.getUsername());
        }
        
        return vo;
    }
}

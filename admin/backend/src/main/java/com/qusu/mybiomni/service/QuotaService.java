package com.qusu.mybiomni.service;

import com.qusu.mybiomni.controller.admin.response.QuotaVO;
import com.qusu.mybiomni.dao.mysql.dao.UserQuotaDAO;
import com.qusu.mybiomni.dao.mysql.model.UserQuotaDO;
import com.qusu.mybiomni.dao.mysql.model.UserQuotaDOExample;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Date;
import java.util.List;

/**
 * 配额管理服务
 */
@Service
public class QuotaService {
    
    @Autowired
    private UserQuotaDAO userQuotaDAO;
    
    /**
     * 获取用户配额
     */
    public QuotaVO getUserQuota(Integer userId) {
        UserQuotaDOExample example = new UserQuotaDOExample();
        example.createCriteria().andUserIdEqualTo(userId);
        
        List<UserQuotaDO> quotas = userQuotaDAO.selectByExample(example);
        
        if (quotas.isEmpty()) {
            // 如果没有配额记录，创建默认配额
            return createDefaultQuota(userId);
        }
        
        UserQuotaDO quotaDO = quotas.get(0);
        return convertToVO(quotaDO);
    }
    
    /**
     * 创建默认配额
     */
    @Transactional
    public QuotaVO createDefaultQuota(Integer userId) {
        UserQuotaDO quotaDO = new UserQuotaDO();
        quotaDO.setUserId(userId);
        quotaDO.setTotalTokenLimit(1000000); // 默认 100 万
        quotaDO.setTotalTokenUsed(0);
        quotaDO.setCreatedAt(new Date());
        quotaDO.setUpdatedAt(new Date());
        
        userQuotaDAO.insert(quotaDO);
        
        return convertToVO(quotaDO);
    }
    
    /**
     * 更新用户配额
     */
    @Transactional
    public void updateQuota(Integer userId, Integer totalTokenLimit) {
        UserQuotaDOExample example = new UserQuotaDOExample();
        example.createCriteria().andUserIdEqualTo(userId);
        
        List<UserQuotaDO> quotas = userQuotaDAO.selectByExample(example);
        
        if (quotas.isEmpty()) {
            // 如果没有配额记录，创建新记录
            UserQuotaDO quotaDO = new UserQuotaDO();
            quotaDO.setUserId(userId);
            quotaDO.setTotalTokenLimit(totalTokenLimit);
            quotaDO.setTotalTokenUsed(0);
            quotaDO.setCreatedAt(new Date());
            quotaDO.setUpdatedAt(new Date());
            userQuotaDAO.insert(quotaDO);
        } else {
            // 更新现有记录
            UserQuotaDO quotaDO = quotas.get(0);
            quotaDO.setTotalTokenLimit(totalTokenLimit);
            quotaDO.setUpdatedAt(new Date());
            userQuotaDAO.updateByPrimaryKeySelective(quotaDO);
        }
    }
    
    /**
     * 重置用户配额使用量
     */
    @Transactional
    public void resetQuota(Integer userId) {
        UserQuotaDOExample example = new UserQuotaDOExample();
        example.createCriteria().andUserIdEqualTo(userId);
        
        List<UserQuotaDO> quotas = userQuotaDAO.selectByExample(example);
        
        if (!quotas.isEmpty()) {
            UserQuotaDO quotaDO = quotas.get(0);
            quotaDO.setTotalTokenUsed(0);
            quotaDO.setUpdatedAt(new Date());
            userQuotaDAO.updateByPrimaryKeySelective(quotaDO);
        }
    }
    
    /**
     * 转换为 VO
     */
    private QuotaVO convertToVO(UserQuotaDO quotaDO) {
        QuotaVO vo = new QuotaVO();
        vo.setId(quotaDO.getId());
        vo.setUserId(quotaDO.getUserId());
        vo.setTotalTokenLimit(quotaDO.getTotalTokenLimit());
        vo.setTotalTokenUsed(quotaDO.getTotalTokenUsed());
        
        // 计算剩余和使用率
        int remaining = quotaDO.getTotalTokenLimit() - quotaDO.getTotalTokenUsed();
        vo.setRemaining(remaining);
        
        if (quotaDO.getTotalTokenLimit() > 0) {
            double usagePercent = (double) quotaDO.getTotalTokenUsed() / quotaDO.getTotalTokenLimit() * 100;
            vo.setUsagePercent(Math.round(usagePercent * 100.0) / 100.0); // 保留两位小数
        } else {
            vo.setUsagePercent(0.0);
        }
        
        vo.setCreatedAt(quotaDO.getCreatedAt());
        vo.setUpdatedAt(quotaDO.getUpdatedAt());
        
        return vo;
    }
}

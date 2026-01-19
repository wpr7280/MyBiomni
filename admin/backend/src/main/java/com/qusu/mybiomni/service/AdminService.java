package com.qusu.mybiomni.service;

import com.google.common.cache.Cache;
import com.google.common.cache.CacheBuilder;
import com.qusu.mybiomni.common.constant.AdminStatus;
import com.qusu.mybiomni.common.constant.ForcePasswordChange;
import com.qusu.mybiomni.common.util.JWTUtils;
import com.qusu.mybiomni.controller.auth.AdminVO;
import com.qusu.mybiomni.dao.mysql.dao.AdminDAO;
import com.qusu.mybiomni.dao.mysql.model.AdminDO;
import com.qusu.mybiomni.dao.mysql.model.AdminDOExample;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Date;
import java.util.List;
import java.util.concurrent.TimeUnit;

@Service
@Slf4j
public class AdminService {

    @Autowired
    private AdminDAO adminDAO;

    private Cache<String, AdminVO> adminCache;

    @PostConstruct
    public void init() {
        adminCache = CacheBuilder.newBuilder()
                .maximumSize(1000)
                .expireAfterWrite(10, TimeUnit.MINUTES)
                .build();
    }


    public AdminVO getCurrentAdmin(String token) {
        String adminId = JWTUtils.getUserIdFromToken(token);
        return getAdminInfo(adminId);
    }

    public AdminDO getAdminById(Integer adminId) {
        return adminDAO.selectByPrimaryKey(adminId);
    }

    public AdminDO getAdminByEmail(String email) {
        AdminDOExample example = new AdminDOExample();
        example.createCriteria().andEmailEqualTo(email).andDeletedAtIsNull();
        List<AdminDO> admins = adminDAO.selectByExample(example);
        if (admins.isEmpty()) {
            return null;
        }
        return admins.get(0);
    }

    public AdminVO getAdminInfo(String adminId) {
        // 优先查缓存
        AdminVO cached = adminCache.getIfPresent(adminId);
        if (cached != null) {
            log.debug("命中管理员缓存: {}", adminId);
            return cached;
        }

        // 查数据库
        AdminDO admin = adminDAO.selectByPrimaryKey(Integer.parseInt(adminId));
        if (admin == null) {
            throw new RuntimeException("管理员不存在");
        }

        AdminVO adminVO = new AdminVO();
        adminVO.setId(admin.getId());
        adminVO.setEmail(admin.getEmail());
        adminVO.setUsername(admin.getUsername());
        adminVO.setStatus(AdminStatus.isActive(admin.getStatus()) ? "ACTIVE" : "INACTIVE");
        adminVO.setCreateTime(admin.getCreatedAt());
        adminVO.setRealName(admin.getRealName());
        adminVO.setAvatar(admin.getAvatar());
        adminVO.setForcePasswordChange(ForcePasswordChange.needChange(admin.getForcePasswordChange()));

        adminCache.put(adminId, adminVO); // 加入缓存
        return adminVO;
    }

    // 清除缓存（如管理员信息修改时）
    public void evictAdminCache(String adminId) {
        adminCache.invalidate(adminId);
    }


    public void updatePassword(Integer adminId, String passwordHash) {
        AdminDO admin = new AdminDO();
        admin.setId(adminId);
        admin.setPassword(passwordHash);
        admin.setUpdatedAt(new Date());
        adminDAO.updateByPrimaryKeySelective(admin);
        evictAdminCache(String.valueOf(adminId));
    }

    public void updateLastLogin(Integer adminId) {
        AdminDO admin = new AdminDO();
        admin.setId(adminId);
        admin.setLastLoginAt(new Date());
        // 重置登录失败次数
        admin.setLoginFailCount(0);
        adminDAO.updateByPrimaryKeySelective(admin);
        evictAdminCache(String.valueOf(adminId));
    }

    public void clearForcePasswordChange(Integer adminId) {
        AdminDO admin = new AdminDO();
        admin.setId(adminId);
        admin.setForcePasswordChange(ForcePasswordChange.NO.getCode());
        admin.setUpdatedAt(new Date());
        adminDAO.updateByPrimaryKeySelective(admin);
        evictAdminCache(String.valueOf(adminId));
    }
}
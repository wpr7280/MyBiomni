package com.qusu.mybiomni.service;

import com.qusu.mybiomni.common.constant.AdminStatus;
import com.qusu.mybiomni.common.constant.ForcePasswordChange;
import com.qusu.mybiomni.dao.mysql.model.AdminDO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import com.qusu.mybiomni.controller.auth.LoginResponse;
import com.qusu.mybiomni.common.util.JWTUtils;

@Service
public class AuthService {

    @Autowired
    private AdminService adminService;

    @Autowired
    private PasswordEncoder passwordEncoder;


    public LoginResponse login(String email, String password) {
        AdminDO admin = adminService.getAdminByEmail(email);
        if (admin == null) {
            throw new RuntimeException("管理员不存在");
        }

        if (!passwordEncoder.matches(password, admin.getPassword())) {
            throw new RuntimeException("密码错误");
        }

        // 检查状态：使用枚举
        if (!AdminStatus.isActive(admin.getStatus())) {
            throw new RuntimeException("管理员状态异常");
        }

        // 检查是否被锁定
        if (admin.getLockedUntil() != null && admin.getLockedUntil().after(new java.util.Date())) {
            throw new RuntimeException("账号已被锁定，请稍后再试");
        }

        String token = JWTUtils.generateToken(String.valueOf(admin.getId()), admin.getEmail());

        LoginResponse response = new LoginResponse();
        response.setToken(token);
        response.setUserId(String.valueOf(admin.getId()));
        response.setEmail(admin.getEmail());
        response.setUsername(admin.getUsername());
        response.setRole(admin.getRole() != null ? admin.getRole() : "user");
        response.setForcePasswordChange(ForcePasswordChange.needChange(admin.getForcePasswordChange()));

        // 更新最后登录时间
        adminService.updateLastLogin(admin.getId());

        return response;
    }

    public void logout(Integer adminId) {
        adminService.evictAdminCache(String.valueOf(adminId));
    }

    public boolean updatePassword(Integer adminId, String oldPassword, String newPassword) {
        AdminDO admin = adminService.getAdminById(adminId);
        if (admin == null) {
            throw new RuntimeException("管理员不存在");
        }

        if (!passwordEncoder.matches(oldPassword, admin.getPassword())) {
            throw new RuntimeException("原密码错误");
        }

        String passwordHash = passwordEncoder.encode(newPassword);
        adminService.updatePassword(adminId, passwordHash);
        
        // 如果是首次修改密码，清除强制修改密码标记
        if (ForcePasswordChange.needChange(admin.getForcePasswordChange())) {
            adminService.clearForcePasswordChange(adminId);
        }
        
        return true;
    }

    /**
     * 更新用户信息（用户名和邮箱）
     * @param adminId 管理员ID
     * @param username 用户名（可选）
     * @param email 邮箱（可选）
     */
    public void updateUserInfo(Integer adminId, String username, String email) {
        AdminDO admin = adminService.getAdminById(adminId);
        if (admin == null) {
            throw new RuntimeException("管理员不存在");
        }

        boolean needUpdate = false;
        AdminDO updateAdmin = new AdminDO();
        updateAdmin.setId(adminId);

        // 更新用户名
        if (username != null && !username.trim().isEmpty() && !username.equals(admin.getUsername())) {
            updateAdmin.setUsername(username.trim());
            needUpdate = true;
        }

        // 更新邮箱
        if (email != null && !email.trim().isEmpty() && !email.equals(admin.getEmail())) {
            // 检查邮箱是否已被其他管理员使用
            AdminDO existingAdmin = adminService.getAdminByEmail(email);
            if (existingAdmin != null && !existingAdmin.getId().equals(adminId)) {
                throw new RuntimeException("Email already in use");
            }
            updateAdmin.setEmail(email.trim());
            needUpdate = true;
        }

        if (needUpdate) {
            updateAdmin.setUpdatedAt(new java.util.Date());
            adminService.updateAdminInfo(updateAdmin);
        }
    }
}

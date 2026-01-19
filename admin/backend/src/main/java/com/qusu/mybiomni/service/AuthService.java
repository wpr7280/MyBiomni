package com.qusu.mybiomni.service;

import com.qusu.mybiomni.common.constant.UserStatus;
import com.qusu.mybiomni.common.response.auth.LoginResponse;
import com.qusu.mybiomni.common.util.JWTUtils;
import com.qusu.mybiomni.dao.mysql.model.UserDO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Date;
import java.util.UUID;

@Service
public class AuthService {

    @Autowired
    private UserService userService;

    @Autowired
    private PasswordEncoder passwordEncoder;


    public LoginResponse login(String email, String password) {
        UserDO user = userService.getUserByEmail(email);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }

        if (!passwordEncoder.matches(password, user.getPasswordHash())) {
            throw new RuntimeException("密码错误");
        }

        if (!UserStatus.ACTIVE.name().equals(user.getStatus())) {
            throw new RuntimeException("用户状态异常");
        }

        String token = JWTUtils.generateToken(user.getId(), user.getEmail());

        LoginResponse response = new LoginResponse();
        response.setToken(token);
        response.setUserId(user.getId());
        response.setEmail(user.getEmail());
        response.setUsername(user.getUsername());

        return response;
    }

    public void logout(String userId) {
        userService.evictUserCache(userId);
    }

    public boolean updatePassword(String userId, String oldPassword, String newPassword) {
        UserDO user = userService.getUserById(userId);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }

        if (!passwordEncoder.matches(oldPassword, user.getPasswordHash())) {
            throw new RuntimeException("原密码错误");
        }

        String passwordHash = passwordEncoder.encode(newPassword);
        userService.updatePassword(user.getId(), passwordHash);
        return true;
    }

    /**
     * 通过邮箱重置密码
     * @param email 邮箱地址
     * @param newPassword 新密码
     * @return 重置是否成功
     */
    public boolean resetPassword(String email, String newPassword) {
        UserDO user = userService.getUserByEmail(email);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }

        if (!UserStatus.ACTIVE.name().equals(user.getStatus())) {
            throw new RuntimeException("用户状态异常，无法重置密码");
        }

        String passwordHash = passwordEncoder.encode(newPassword);
        userService.updatePassword(user.getId(), passwordHash);
        
        // 清除用户缓存，强制用户重新登录
        userService.evictUserCache(user.getId());
        
        return true;
    }
}
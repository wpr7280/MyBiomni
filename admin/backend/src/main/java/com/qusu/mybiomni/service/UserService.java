package com.qusu.mybiomni.service;

import com.google.common.cache.Cache;
import com.google.common.cache.CacheBuilder;
import com.qusu.mybiomni.common.util.JWTUtils;
import com.qusu.mybiomni.controller.auth.UserVO;
import com.qusu.mybiomni.dao.mysql.dao.UserDAO;
import com.qusu.mybiomni.dao.mysql.model.UserDO;
import com.qusu.mybiomni.dao.mysql.model.UserDOExample;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.concurrent.TimeUnit;

@Service
@Slf4j
public class UserService {

    @Autowired
    private UserDAO userDAO;

    private Cache<String, UserVO> userCache;

    @PostConstruct
    public void init() {
        userCache = CacheBuilder.newBuilder()
                .maximumSize(1000)
                .expireAfterWrite(10, TimeUnit.MINUTES)
                .build();
    }


    public UserVO getCurrentUser(String token) {
        String userId = JWTUtils.getUserIdFromToken(token);
        return getUserInfo(userId);
    }

    public UserDO getUserById(String userId) {
        return userDAO.selectByPrimaryKey(userId);
    }

    public UserDO getUserByEmail(String email) {
        UserDOExample example = new UserDOExample();
        example.createCriteria().andEmailEqualTo(email);
        List<UserDO> users = userDAO.selectByExample(example);
        if (users.isEmpty()) {
            return null;
        }
        return users.get(0);
    }

    public UserVO getUserInfo(String userId) {
        // 优先查缓存
        UserVO cached = userCache.getIfPresent(userId);
        if (cached != null) {
            log.debug("命中用户缓存: {}", userId);
            return cached;
        }

        // 查数据库
        UserDO user = userDAO.selectByPrimaryKey(userId);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }

        UserVO userVO = new UserVO();
        userVO.setId(user.getId());
        userVO.setEmail(user.getEmail());
        userVO.setUsername(user.getUsername());
        userVO.setStatus(user.getStatus());
        userVO.setCreateTime(user.getCreateTime());

        userCache.put(userId, userVO); // 加入缓存
        return userVO;
    }

    // 可选：用于清除缓存（如用户信息修改时）
    public void evictUserCache(String userId) {
        userCache.invalidate(userId);
    }


    public void updateUserName(String userId, String username) {
        UserDO user = new UserDO();
        user.setId(userId);
        user.setUsername(username);
        userDAO.updateByPrimaryKeySelective(user);
        evictUserCache(userId);
    }

    public void updatePassword(String userId, String passwordHash) {
        UserDO user = new UserDO();
        user.setId(userId);
        user.setPasswordHash(passwordHash);
        userDAO.updateByPrimaryKeySelective(user);
    }
}
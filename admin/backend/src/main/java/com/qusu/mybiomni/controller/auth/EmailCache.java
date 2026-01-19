package com.qusu.mybiomni.controller.auth;


import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.util.concurrent.TimeUnit;

@Slf4j
@Component
public class EmailCache {
    private static final String KEY_PREFIX = "email:verify:";
    private static final int EXPIRE_TIME_MINUTES = 15; // 15分钟过期

    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    /**
     * 存储验证码，支持类型区分
     * @param email 邮箱地址
     * @param code 验证码
     * @param type 类型（register, forgetPwd等）
     */
    public void put(String email, String code, String type) {
        String key = buildKey(email, type);
        try {
            redisTemplate.opsForValue().set(key, code, Duration.ofMinutes(EXPIRE_TIME_MINUTES));
            log.debug("存储验证码成功 - email: {}, type: {}, key: {}", email, type, key);
        } catch (Exception e) {
            log.error("存储验证码失败 - email: {}, type: {}, error: {}", email, type, e.getMessage(), e);
            throw new RuntimeException("验证码存储失败", e);
        }
    }

    /**
     * 兼容旧方法，默认类型为register
     */
    public void put(String email, String code) {
        put(email, code, "register");
    }

    /**
     * 获取验证码，支持类型区分
     * @param email 邮箱地址
     * @param type 类型（register, forgetPwd等）
     * @return 验证码，如果不存在或已过期返回null
     */
    public String get(String email, String type) {
        String key = buildKey(email, type);
        try {
            String code = redisTemplate.opsForValue().get(key);
            if (code != null) {
                log.debug("获取验证码成功 - email: {}, type: {}, key: {}", email, type, key);
                return code;
            } else {
                log.debug("验证码不存在或已过期 - email: {}, type: {}, key: {}", email, type, key);
                return null;
            }
        } catch (Exception e) {
            log.error("获取验证码失败 - email: {}, type: {}, error: {}", email, type, e.getMessage(), e);
            return null;
        }
    }

    /**
     * 兼容旧方法，默认类型为register
     */
    public String get(String email) {
        return get(email, "register");
    }


    /**
     * 构建缓存key，格式为 "email:type"
     */
    private String buildKey(String email, String type) {
        return email + ":" + (type != null ? type : "register");
    }


    /**
     * 移除指定邮箱和类型的验证码
     */
    public void remove(String email, String type) {
        String key = buildKey(email, type);
        try {
            Boolean result = redisTemplate.delete(key);
            log.debug("删除验证码 - email: {}, type: {}, key: {}, result: {}", email, type, key, result);
        } catch (Exception e) {
            log.error("删除验证码失败 - email: {}, type: {}, error: {}", email, type, e.getMessage(), e);
        }
    }
    /**
     * 检查验证码是否存在
     */
    public boolean exists(String email, String type) {
        String key = buildKey(email, type);
        try {
            Boolean exists = redisTemplate.hasKey(key);
            return exists != null && exists;
        } catch (Exception e) {
            log.error("检查验证码存在性失败 - email: {}, type: {}, error: {}", email, type, e.getMessage(), e);
            return false;
        }
    }

    /**
     * 获取验证码剩余过期时间（秒）
     */
    public Long getExpireTime(String email, String type) {
        String key = buildKey(email, type);
        try {
            return redisTemplate.getExpire(key, TimeUnit.SECONDS);
        } catch (Exception e) {
            log.error("获取验证码过期时间失败 - email: {}, type: {}, error: {}", email, type, e.getMessage(), e);
            return null;
        }
    }

}

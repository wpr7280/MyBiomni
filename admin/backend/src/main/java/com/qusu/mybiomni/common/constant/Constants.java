package com.qusu.mybiomni.common.constant;

import java.util.Set;

public class Constants {
    /**
     * 不需要认证的 URL（公开接口）
     */
    public static final Set<String> NO_NEED_AUTH_URL = Set.of(
            "/api/auth/login",
            "/health/alive"
    );

    /**
     * 静态资源路径前缀
     */
    public static final String[] STATIC_RESOURCE_PATTERNS = {
            "/static/**",
            "/uploads/**",
    };

}

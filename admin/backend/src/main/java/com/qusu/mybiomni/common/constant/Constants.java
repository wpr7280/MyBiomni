package com.qusu.mybiomni.common.constant;

import java.util.Set;

public class Constants {
    public static final Set<String> NO_NEED_AUTH_URL = Set.of(
            "/api/auth/login",  "/api/auth/sendEmail",
            "/api/auth/logout", "/api/auth/resetPassword",
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

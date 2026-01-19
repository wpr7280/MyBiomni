package com.qusu.mybiomni.common.constant;

/**
 * 用户角色枚举
 * 统一管理员和普通用户，通过角色区分权限
 */
public enum UserRole {
    ADMIN("admin", "管理员"),
    USER("user", "普通用户");

    private final String code;
    private final String description;

    UserRole(String code, String description) {
        this.code = code;
        this.description = description;
    }

    public String getCode() {
        return code;
    }

    public String getDescription() {
        return description;
    }

    /**
     * 根据 code 获取枚举
     */
    public static UserRole fromCode(String code) {
        if (code == null) {
            return null;
        }
        for (UserRole role : values()) {
            if (role.code.equals(code)) {
                return role;
            }
        }
        return null;
    }

    /**
     * 判断是否为管理员
     */
    public static boolean isAdmin(String code) {
        return ADMIN.code.equals(code);
    }

    /**
     * 判断是否可以访问管理功能
     */
    public static boolean canAccessAdmin(String code) {
        return ADMIN.code.equals(code);
    }

    /**
     * 判断是否为普通用户
     */
    public static boolean isUser(String code) {
        return USER.code.equals(code);
    }
}

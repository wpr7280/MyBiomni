package com.qusu.mybiomni.common.constant;

/**
 * 管理员角色枚举
 */
public enum AdminRole {
    SUPER_ADMIN("super_admin", "超级管理员"),
    ADMIN("admin", "普通管理员");

    private final String code;
    private final String description;

    AdminRole(String code, String description) {
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
    public static AdminRole fromCode(String code) {
        if (code == null) {
            return null;
        }
        for (AdminRole role : values()) {
            if (role.code.equals(code)) {
                return role;
            }
        }
        return null;
    }

    /**
     * 判断是否为超级管理员
     */
    public static boolean isSuperAdmin(String code) {
        return SUPER_ADMIN.code.equals(code);
    }
}

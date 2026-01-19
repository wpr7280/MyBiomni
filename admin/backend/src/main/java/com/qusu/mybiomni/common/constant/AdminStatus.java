package com.qusu.mybiomni.common.constant;

/**
 * 管理员状态枚举
 */
public enum AdminStatus {
    DISABLED(0, "禁用"),
    ACTIVE(1, "启用");

    private final Integer code;
    private final String description;

    AdminStatus(Integer code, String description) {
        this.code = code;
        this.description = description;
    }

    public Integer getCode() {
        return code;
    }

    public String getDescription() {
        return description;
    }

    /**
     * 根据 code 获取枚举
     */
    public static AdminStatus fromCode(Integer code) {
        if (code == null) {
            return null;
        }
        for (AdminStatus status : values()) {
            if (status.code.equals(code)) {
                return status;
            }
        }
        return null;
    }

    /**
     * 判断是否为启用状态
     */
    public static boolean isActive(Integer code) {
        return ACTIVE.code.equals(code);
    }
}

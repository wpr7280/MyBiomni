package com.qusu.mybiomni.common.constant;

/**
 * 强制修改密码标记枚举
 */
public enum ForcePasswordChange {
    NO(0, "不需要"),
    YES(1, "需要强制修改");

    private final Integer code;
    private final String description;

    ForcePasswordChange(Integer code, String description) {
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
    public static ForcePasswordChange fromCode(Integer code) {
        if (code == null) {
            return null;
        }
        for (ForcePasswordChange status : values()) {
            if (status.code.equals(code)) {
                return status;
            }
        }
        return null;
    }

    /**
     * 判断是否需要强制修改密码
     */
    public static boolean needChange(Integer code) {
        return YES.code.equals(code);
    }
}

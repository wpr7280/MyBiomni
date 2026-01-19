package com.qusu.mybiomni.common.util;

public class PasswordValidator {

    // 正则表达式：确保密码至少包含 6 个字母或者数字
    private static final String PASSWORD_PATTERN = "^[a-zA-Z@0-9]{6,}$";

    public static boolean isValidPassword(String password) {
        if (password == null) {
            return false;
        }
        return password.matches(PASSWORD_PATTERN);
    }
}

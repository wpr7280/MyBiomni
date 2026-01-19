package com.qusu.mybiomni.common.util;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

/**
 * 密码生成工具类
 * 用于生成 BCrypt 加密的密码
 */
public class PasswordGenerator {

    public static void main(String[] args) {
        BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();
        
        // 生成默认管理员密码
        String[] passwords = {
            "Admin@123456"
        };
        
        System.out.println("=".repeat(80));
        System.out.println("BCrypt 密码生成工具");
        System.out.println("=".repeat(80));
        
        for (String password : passwords) {
            String hashedPassword = encoder.encode(password);
            System.out.println("\n原始密码: " + password);
            System.out.println("BCrypt 哈希: " + hashedPassword);
            System.out.println("-".repeat(80));
        }
        
        System.out.println("\n使用方法:");
        System.out.println("1. 复制上面生成的 BCrypt 哈希值");
        System.out.println("2. 替换 SQL 文件中的 password 字段值");
        System.out.println("3. 执行 SQL 插入管理员账号");
        System.out.println("=".repeat(80));
        
        // 验证密码
        System.out.println("\n验证示例:");
        String testPassword = "Admin@123456";
        String testHash = encoder.encode(testPassword);
        boolean matches = encoder.matches(testPassword, testHash);
        System.out.println("密码: " + testPassword);
        System.out.println("哈希: " + testHash);
        System.out.println("验证结果: " + (matches ? "✓ 匹配" : "✗ 不匹配"));
        System.out.println("=".repeat(80));
    }
}

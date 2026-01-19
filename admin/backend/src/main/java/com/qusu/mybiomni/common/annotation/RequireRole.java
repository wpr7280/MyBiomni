package com.qusu.mybiomni.common.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 角色权限注解
 * 用于标记需要特定角色才能访问的接口
 * 
 * 使用示例:
 * @RequireRole("admin")  // 只有管理员可以访问
 * @RequireRole({"admin", "user"})  // 管理员和用户都可以访问
 */
@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface RequireRole {
    /**
     * 允许访问的角色列表
     * 可选值: "admin", "user"
     */
    String[] value() default {};
}

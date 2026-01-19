package com.qusu.mybiomni.common.interceptor;

import com.qusu.mybiomni.common.annotation.RequireRole;
import com.qusu.mybiomni.controller.auth.AdminVO;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.HandlerInterceptor;

import java.util.Arrays;

/**
 * 角色权限检查拦截器
 * 配合 @RequireRole 注解使用
 */
@Component
@Slf4j
public class RoleCheckInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        // 只处理 Controller 方法
        if (!(handler instanceof HandlerMethod)) {
            return true;
        }

        HandlerMethod handlerMethod = (HandlerMethod) handler;
        
        // 检查方法上的 @RequireRole 注解
        RequireRole methodAnnotation = handlerMethod.getMethodAnnotation(RequireRole.class);
        
        // 检查类上的 @RequireRole 注解
        RequireRole classAnnotation = handlerMethod.getBeanType().getAnnotation(RequireRole.class);
        
        // 如果都没有注解，放行
        if (methodAnnotation == null && classAnnotation == null) {
            return true;
        }

        // 获取当前用户
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.getWriter().write("{\"code\":401,\"message\":\"未登录\"}");
            return false;
        }

        AdminVO currentUser = (AdminVO) authentication.getPrincipal();
        String userRole = currentUser.getRole() != null ? currentUser.getRole() : "user";

        // 获取需要的角色（方法注解优先于类注解）
        String[] requiredRoles = methodAnnotation != null ? methodAnnotation.value() : classAnnotation.value();

        // 检查用户角色是否在允许的角色列表中
        boolean hasPermission = Arrays.asList(requiredRoles).contains(userRole);

        if (!hasPermission) {
            log.warn("用户 {} (角色: {}) 尝试访问需要 {} 角色的接口: {}", 
                    currentUser.getUsername(), userRole, Arrays.toString(requiredRoles), request.getRequestURI());
            response.setStatus(HttpServletResponse.SC_FORBIDDEN);
            response.setContentType("application/json;charset=UTF-8");
            response.getWriter().write("{\"code\":403,\"message\":\"权限不足\"}");
            return false;
        }

        return true;
    }
}

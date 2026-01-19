package com.qusu.mybiomni.common.interceptor;

import com.qusu.mybiomni.common.constant.Constants;
import com.qusu.mybiomni.common.util.TenantContextUtil;
import com.qusu.mybiomni.controller.auth.AdminVO;
import com.qusu.mybiomni.service.AdminService;
import com.qusu.mybiomni.common.util.JWTUtils;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Collections;

@Component
@Slf4j
public class TokenAuthFilter extends OncePerRequestFilter {
    @Autowired
    AdminService adminService;
    private static final String AUTHORIZATION_HEADER = "Authorization";
    private static final String BEARER_PREFIX = "Bearer ";

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain) throws ServletException, IOException {
        try {
            // 1. 提取JWT Token
            String token = extractTokenFromRequest(request);
            if (token != null) {
                // 2. 验证Token有效性
                if (JWTUtils.validateToken(token)) {
                    // 3. 提取管理员信息
                    String adminId = JWTUtils.getUserIdFromToken(token);
                    String email = JWTUtils.getEmailFromToken(token);
                    // 4. 设置管理员上下文
                    setAdminContext(adminId, email, token);
                    log.info("Token验证成功，管理员ID: {}, 邮箱: {}", adminId, email);
                } else {
                    log.warn("Token验证失败: {}", token);
                    clearSecurityContext();
                }
            }
        } catch (Exception e) {
            log.error("Token处理异常: ", e);
            clearSecurityContext();
        }
        // 5. 继续过滤链
        filterChain.doFilter(request, response);
    }

    /**
     * 从请求中提取Token
     */
    private String extractTokenFromRequest(HttpServletRequest request) {
        // 优先从Header中获取
        String bearerToken = request.getHeader(AUTHORIZATION_HEADER);
        if (StringUtils.hasText(bearerToken) && bearerToken.startsWith(BEARER_PREFIX)) {
            return bearerToken.substring(BEARER_PREFIX.length());
        }

        // 备选：从请求参数中获取
        String tokenParam = request.getHeader("Token");
        if (StringUtils.hasText(tokenParam)) {
            return tokenParam;
        }
        return null;
    }

    /**
     * 设置管理员认证上下文
     */
    private void setAdminContext(String adminId, String email, String token) {
        // 设置Spring Security认证信息
        AdminVO admin = adminService.getAdminInfo(adminId);
        admin.setToken(token);
        UsernamePasswordAuthenticationToken authentication = new UsernamePasswordAuthenticationToken(
            admin, 
            token, 
            Collections.singletonList(new SimpleGrantedAuthority("ROLE_ADMIN"))
        );
        SecurityContextHolder.getContext().setAuthentication(authentication);
        // 设置租户上下文（多租户支持）
        TenantContextUtil.setCurrentUserId(adminId);
    }

    /**
     * 清除安全上下文
     */
    private void clearSecurityContext() {
        SecurityContextHolder.clearContext();
        TenantContextUtil.clear();
    }

    /**
     * 判断是否跳过Token验证
     */
    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) throws ServletException {
        String path = request.getRequestURI();
        String method = request.getMethod();

        // 跳过认证的路径
        return isPublicPath(path, method);
    }

    /**
     * 判断是否为公开路径
     */
    private boolean isPublicPath(String path, String method) {
        // 公开的API接口
        if (Constants.NO_NEED_AUTH_URL.contains(path)) {
            return true;
        }

        // 静态资源（使用通配符匹配）
        for (String pattern : Constants.STATIC_RESOURCE_PATTERNS) {
            if (matchesPattern(path, pattern)) {
                return true;
            }
        }
        // Actuator监控接口
        if (path.startsWith("/actuator/")) {
            return true;
        }
        // OPTIONS请求（CORS预检）
        if ("OPTIONS".equalsIgnoreCase(method)) {
            return true;
        }
        return false;
    }

    /**
     * 简单的路径匹配（支持 ** 通配符）
     */
    private boolean matchesPattern(String path, String pattern) {
        if (pattern.endsWith("/**")) {
            String prefix = pattern.substring(0, pattern.length() - 3);
            return path.startsWith(prefix);
        }
        return path.equals(pattern);
    }

}
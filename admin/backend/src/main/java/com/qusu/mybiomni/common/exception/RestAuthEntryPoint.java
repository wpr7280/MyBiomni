package com.qusu.mybiomni.common.exception;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;

import java.io.IOException;
import java.util.Map;

public class RestAuthEntryPoint implements AuthenticationEntryPoint {

    @Override
    public void commence(HttpServletRequest req,
                         HttpServletResponse res,
                         AuthenticationException ex) throws IOException {

        res.setStatus(HttpServletResponse.SC_UNAUTHORIZED);  // 401
        res.setContentType("application/json;charset=UTF-8");

        var body = Map.of(
                "code", 401,
                "message", "未登录或 token 无效"
        );
        res.getWriter().write(new ObjectMapper().writeValueAsString(body));
    }
}
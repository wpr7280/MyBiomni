package com.qusu.mybiomni.common.exception;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.web.access.AccessDeniedHandler;

import java.io.IOException;
import java.util.Map;

public class RestAccessDeniedHandler implements AccessDeniedHandler {

    @Override
    public void handle(HttpServletRequest req,
                       HttpServletResponse res,
                       AccessDeniedException ex) throws IOException {

        res.setStatus(HttpServletResponse.SC_FORBIDDEN);     // 403
        res.setContentType("application/json;charset=UTF-8");

        var body = Map.of(
                "code", 403,
                "message", "权限不足"
        );
        res.getWriter().write(new ObjectMapper().writeValueAsString(body));
    }
}
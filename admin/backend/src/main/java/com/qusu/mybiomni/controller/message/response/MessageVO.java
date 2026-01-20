package com.qusu.mybiomni.controller.message.response;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class MessageVO {
    private Integer id;
    private Integer conversationId;
    private String role;
    private String content;
    private String contentType;
    private Integer tokens;
    private Integer inputTokens;
    private Integer outputTokens;
    private LocalDateTime createdAt;
}

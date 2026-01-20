package com.qusu.mybiomni.controller.conversation.response;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class ConversationVO {
    private Integer id;
    private String title;
    private String status;
    private Integer messageCount;
    private Integer totalTokens;
    private Integer totalDurationMs;
    private LocalDateTime lastMessageAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}

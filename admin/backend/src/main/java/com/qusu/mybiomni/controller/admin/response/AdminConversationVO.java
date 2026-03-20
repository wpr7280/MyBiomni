package com.qusu.mybiomni.controller.admin.response;

import lombok.Data;

import java.util.Date;

/**
 * 管理员查看对话 VO
 */
@Data
public class AdminConversationVO {
    private Integer id;
    private Integer userId;
    private String userEmail;
    private String username;
    private String title;
    private String status;
    private Integer messageCount;
    private Integer totalTokens;
    private Integer totalDurationMs;
    private Date lastMessageAt;
    private Date createdAt;
    private Date updatedAt;
    private Date deletedAt;
    private Boolean deleted;
}

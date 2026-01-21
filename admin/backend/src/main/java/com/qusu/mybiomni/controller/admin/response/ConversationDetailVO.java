package com.qusu.mybiomni.controller.admin.response;

import lombok.Data;

import java.util.Date;
import java.util.List;

/**
 * 对话详情 VO
 */
@Data
public class ConversationDetailVO {
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
    
    // 消息列表
    private List<MessageVO> messages;
    
    @Data
    public static class MessageVO {
        private Integer id;
        private String role;  // user / assistant
        private String content;
        private String contentType;  // text / markdown
        private Integer tokens;
        private Integer inputTokens;
        private Integer outputTokens;
        private Date createdAt;
    }
}

package com.qusu.mybiomni.controller.admin.request;

import lombok.Data;

/**
 * 管理员查看对话列表请求
 */
@Data
public class AdminConversationListRequest {
    
    private Integer currentPage = 1;
    private Integer pageSize = 20;
    
    // 搜索关键词（对话标题）
    private String keyword;
    
    // 用户ID筛选
    private Integer userId;
    
    // 用户邮箱筛选
    private String userEmail;
    
    // 状态筛选
    private String status;
    
    // 开始时间
    private String startDate;
    
    // 结束时间
    private String endDate;
    
    public int getStart() {
        return (currentPage - 1) * pageSize;
    }
}

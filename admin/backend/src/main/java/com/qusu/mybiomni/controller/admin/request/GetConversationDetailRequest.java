package com.qusu.mybiomni.controller.admin.request;

import lombok.Data;

import javax.validation.constraints.NotNull;

/**
 * 获取对话详情请求
 */
@Data
public class GetConversationDetailRequest {
    
    @NotNull(message = "对话ID不能为空")
    private Integer conversationId;
}

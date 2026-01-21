package com.qusu.mybiomni.controller.admin.request;

import lombok.Data;

import javax.validation.constraints.NotNull;

/**
 * 删除对话请求
 */
@Data
public class DeleteConversationRequest {
    
    @NotNull(message = "对话ID不能为空")
    private Integer conversationId;
}

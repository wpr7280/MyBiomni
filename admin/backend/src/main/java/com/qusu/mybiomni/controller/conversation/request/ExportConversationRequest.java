package com.qusu.mybiomni.controller.conversation.request;

import lombok.Data;

import javax.validation.constraints.NotNull;

@Data
public class ExportConversationRequest {
    
    @NotNull(message = "对话ID不能为空")
    private Integer conversationId;
    
    private Boolean includeImages = true;
}

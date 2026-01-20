package com.qusu.mybiomni.controller.conversation.request;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Size;

@Data
public class UpdateConversationTitleRequest {
    
    @NotNull(message = "对话ID不能为空")
    private Integer conversationId;
    
    @NotBlank(message = "对话标题不能为空")
    @Size(max = 52, message = "对话标题不能超过255个字符")
    private String title;
}

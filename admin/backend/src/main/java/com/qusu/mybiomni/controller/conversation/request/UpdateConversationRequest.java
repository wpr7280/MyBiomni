package com.qusu.mybiomni.controller.conversation.request;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;

@Data
public class UpdateConversationRequest {
    
    @NotBlank(message = "对话标题不能为空")
    @Size(max = 255, message = "对话标题不能超过255个字符")
    private String title;
}

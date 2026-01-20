package com.qusu.mybiomni.controller.message.request;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;

@Data
public class SendMessageRequest {
    
    @NotNull(message = "对话ID不能为空")
    private Integer conversationId;
    
    @NotBlank(message = "消息内容不能为空")
    private String content;
}

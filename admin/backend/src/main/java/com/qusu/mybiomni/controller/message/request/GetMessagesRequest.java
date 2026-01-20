package com.qusu.mybiomni.controller.message.request;

import com.qusu.mybiomni.common.request.PageRequest;
import lombok.Data;
import lombok.EqualsAndHashCode;

import javax.validation.constraints.NotNull;

@Data
@EqualsAndHashCode(callSuper = true)
public class GetMessagesRequest extends PageRequest {
    
    @NotNull(message = "对话ID不能为空")
    private Integer conversationId;
}

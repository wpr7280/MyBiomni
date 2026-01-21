package com.qusu.mybiomni.controller.admin.request;

import lombok.Data;

import javax.validation.constraints.NotNull;

/**
 * 重置用户配额请求
 */
@Data
public class ResetQuotaRequest {
    
    @NotNull(message = "用户ID不能为空")
    private Integer userId;
}

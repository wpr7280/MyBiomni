package com.qusu.mybiomni.controller.admin.request;

import lombok.Data;

import javax.validation.constraints.Min;
import javax.validation.constraints.NotNull;

/**
 * 更新用户配额请求
 */
@Data
public class UpdateQuotaRequest {
    
    @NotNull(message = "用户ID不能为空")
    private Integer userId;
    
    @NotNull(message = "Token配额不能为空")
    @Min(value = 0, message = "Token配额不能小于0")
    private Integer totalTokenLimit;
}

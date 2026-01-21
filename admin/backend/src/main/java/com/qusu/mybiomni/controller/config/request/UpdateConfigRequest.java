package com.qusu.mybiomni.controller.config.request;

import lombok.Data;

import javax.validation.constraints.NotBlank;

/**
 * 更新配置请求
 */
@Data
public class UpdateConfigRequest {
    
    @NotBlank(message = "配置键不能为空")
    private String configKey;
    
    private String configValue;
}

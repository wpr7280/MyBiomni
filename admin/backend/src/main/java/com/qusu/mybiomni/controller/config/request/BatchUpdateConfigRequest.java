package com.qusu.mybiomni.controller.config.request;

import lombok.Data;

import javax.validation.constraints.NotNull;
import java.util.Map;

/**
 * 批量更新配置请求
 */
@Data
public class BatchUpdateConfigRequest {
    
    @NotNull(message = "配置不能为空")
    private Map<String, String> configs;
}

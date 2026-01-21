package com.qusu.mybiomni.controller.config.response;

import lombok.Data;

import java.util.Date;

/**
 * 系统配置 VO
 */
@Data
public class SystemConfigVO {
    private Integer id;
    private String configKey;
    private String configValue;
    private String configType;
    private String description;
    private Integer isSensitive;
    private Date createdAt;
    private Date updatedAt;
}

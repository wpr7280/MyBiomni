package com.qusu.mybiomni.controller.admin.response;

import lombok.Data;

import java.util.Date;

/**
 * 配额信息 VO
 */
@Data
public class QuotaVO {
    private Integer id;
    private Integer userId;
    private Integer totalTokenLimit;
    private Integer totalTokenUsed;
    private Integer remaining;
    private Double usagePercent;
    private Date createdAt;
    private Date updatedAt;
}

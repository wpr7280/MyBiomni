package com.qusu.mybiomni.controller.admin.request;

import com.qusu.mybiomni.common.request.PageRequest;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
public class UserListRequest extends PageRequest {
    private String keyword;  // 搜索关键词（用户名或邮箱）
    private String role;     // 角色筛选
    private Integer status;  // 状态筛选
}

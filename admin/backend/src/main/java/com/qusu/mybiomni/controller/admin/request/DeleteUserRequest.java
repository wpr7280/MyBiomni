package com.qusu.mybiomni.controller.admin.request;

import lombok.Data;

import javax.validation.constraints.NotNull;

@Data
public class DeleteUserRequest {
    @NotNull(message = "用户ID不能为空")
    private Integer userId;
}

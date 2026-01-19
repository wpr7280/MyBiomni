package com.qusu.mybiomni.controller.admin.request;

import lombok.Data;
import lombok.EqualsAndHashCode;

import javax.validation.constraints.NotNull;

@Data
@EqualsAndHashCode(callSuper = true)
public class UpdateUserByIdRequest extends UpdateUserRequest {
    @NotNull(message = "用户ID不能为空")
    private Integer userId;
}

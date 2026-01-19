package com.qusu.mybiomni.controller.admin.request;

import lombok.Data;

import javax.validation.constraints.Email;

@Data
public class UpdateUserRequest {
    private String username;
    
    @Email(message = "邮箱格式不正确")
    private String email;
    
    private String realName;
    
    private String role;
    
    private Integer status;
}

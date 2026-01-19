package com.qusu.mybiomni.controller.admin.request;

import lombok.Data;

import javax.validation.constraints.Email;
import javax.validation.constraints.NotBlank;

@Data
public class CreateUserRequest {
    @NotBlank(message = "用户名不能为空")
    private String username;
    
    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    private String email;
    
    private String password;  // 如果为空，使用邮箱前缀作为密码
    
    private String realName;
    
    private String role = "user";  // 默认为普通用户
    
    private Integer status = 1;  // 默认启用
}

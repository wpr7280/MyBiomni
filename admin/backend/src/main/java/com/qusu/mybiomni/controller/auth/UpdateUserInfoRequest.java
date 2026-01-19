package com.qusu.mybiomni.controller.auth;

import lombok.Data;

import javax.validation.constraints.Email;

@Data
public class UpdateUserInfoRequest {
    private String username;
    
    @Email(message = "邮箱格式不正确")
    private String email;
}

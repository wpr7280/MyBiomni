package com.qusu.mybiomni.controller.auth;

import lombok.Data;

@Data
public class ResetPasswordRequest {
    private String email;
    private String verifyCode;
    private String newPassword;
} 
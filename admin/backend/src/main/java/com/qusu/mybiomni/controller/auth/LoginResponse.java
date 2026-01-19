package com.qusu.mybiomni.controller.auth;
import lombok.Data;

@Data
public class LoginResponse {
    private String token;
    private String userId;
    private String email;
    private String username;
    private Boolean forcePasswordChange;
}
package com.qusu.mybiomni.controller.auth;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Email;

@Data
public class LoginRequest {
    @NotBlank
    @Email
    private String email;
    @NotBlank
    private String password;
}

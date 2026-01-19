package com.qusu.mybiomni.controller.auth;

import lombok.Data;

import javax.validation.constraints.NotBlank;
@Data
public class UpdatePasswordRequest {
    @NotBlank
    private String oldPassword;
    @NotBlank
    private String newPassword;
}

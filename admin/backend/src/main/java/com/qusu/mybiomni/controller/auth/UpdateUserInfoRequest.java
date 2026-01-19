package com.qusu.mybiomni.controller.auth;

import lombok.Data;

import javax.validation.constraints.NotBlank;

@Data
public class UpdateUserInfoRequest {
    @NotBlank
    String username;
}

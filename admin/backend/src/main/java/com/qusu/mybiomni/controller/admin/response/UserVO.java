package com.qusu.mybiomni.controller.admin.response;

import lombok.Data;

import java.util.Date;

@Data
public class UserVO {
    private Integer id;
    private String username;
    private String email;
    private String phone;
    private String realName;
    private String avatar;
    private String role;
    private Integer status;
    private Date lastLoginAt;
    private Date createdAt;
}

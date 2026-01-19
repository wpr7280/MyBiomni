package com.qusu.mybiomni.controller.auth;

import lombok.Data;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Collection;
import java.util.Date;
import java.util.List;

@Data
public class AdminVO implements UserDetails {
    private Integer id;
    private String email;
    private String username;
    private String realName;
    private String avatar;
    private String status;
    private Date createTime;
    private String token;
    private Boolean forcePasswordChange;

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return List.of();
    }

    @Override
    public String getPassword() {
        return "";
    }
}

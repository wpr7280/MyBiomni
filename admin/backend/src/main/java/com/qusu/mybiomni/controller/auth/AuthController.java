package com.qusu.mybiomni.controller.auth;

import com.qusu.mybiomni.service.AuthService;
import com.qusu.mybiomni.common.response.BaseResult;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = "*")
public class AuthController {
    @Autowired
    private AuthService authService;

    @Autowired
    EmailCache emailCache;

    @PostMapping("/login")
    public BaseResult<LoginResponse> login(@RequestBody LoginRequest request) {
        try {
            LoginResponse response = authService.login(request.getEmail(), request.getPassword());
            return BaseResult.success(response);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }

    @GetMapping("/me")
    public BaseResult<LoginResponse> getCurrentUser(@AuthenticationPrincipal AdminVO admin) {
        try {
            LoginResponse response = new LoginResponse();
            response.setToken(admin.getToken());
            response.setUserId(String.valueOf(admin.getId()));
            response.setEmail(admin.getEmail());
            response.setUsername(admin.getUsername());
            response.setRole(admin.getRole());
            response.setForcePasswordChange(admin.getForcePasswordChange());
            return BaseResult.success(response);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }

    @PostMapping("/logout")
    public BaseResult<Void> logout(@AuthenticationPrincipal AdminVO admin) {
        try {
            authService.logout(admin.getId());
            return BaseResult.success(null);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }


    @PostMapping("/updatePassword")
    public BaseResult<Boolean> updatePassword(@RequestBody UpdatePasswordRequest request, @AuthenticationPrincipal AdminVO admin) {
        try {
            boolean result = authService.updatePassword(admin.getId(), request.getOldPassword(), request.getNewPassword());
            return BaseResult.success(result);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }

    @PostMapping("/updateUserInfo")
    public BaseResult<Void> updateUserInfo(@RequestBody UpdateUserInfoRequest request, @AuthenticationPrincipal AdminVO admin) {
        try {
            authService.updateUserInfo(admin.getId(), request.getUsername(), request.getEmail());
            return BaseResult.success(null);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }
}

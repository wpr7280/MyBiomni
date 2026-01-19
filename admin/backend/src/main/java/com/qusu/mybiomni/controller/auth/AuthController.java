package com.qusu.mybiomni.controller.auth;

import com.qusu.mybiomni.service.AuthService;
import com.qusu.mybiomni.common.response.BaseResult;
import com.qusu.mybiomni.common.response.auth.LoginResponse;
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

    /**
     * 重置密码
     */
    @PostMapping("/resetPassword")
    public BaseResult<Boolean> resetPassword(@RequestBody ResetPasswordRequest request) {
        try {
            // 验证邮箱验证码
            String cachedCode = emailCache.get(request.getEmail(), "forgetPwd");
            if (cachedCode == null) {
                return BaseResult.error("验证码已过期或不存在");
            }
            
            if (!cachedCode.equals(request.getVerifyCode())) {
                return BaseResult.error("验证码错误");
            }
            
            // 重置密码
            boolean result = authService.resetPassword(request.getEmail(), request.getNewPassword());
            
            if (result) {
                // 重置成功后删除验证码，防止重复使用
                emailCache.remove(request.getEmail(), "forgetPwd");
                return BaseResult.success(true);
            } else {
                return BaseResult.error("密码重置失败");
            }
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }

    @GetMapping("/me")
    public BaseResult<LoginResponse> getCurrentUser(@AuthenticationPrincipal UserVO user) {
        try {
            LoginResponse response = new LoginResponse();
            response.setToken(user.getToken());
            response.setUserId(user.getId());
            response.setEmail(user.getEmail());
            response.setUsername(user.getUsername());
            return BaseResult.success(response);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }

    @PostMapping("/logout")
    public BaseResult<Void> logout(@AuthenticationPrincipal UserVO user) {
        try {
            authService.logout(user.getId());
            return BaseResult.success(null);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }


    @PostMapping("/updatePassword")
    public BaseResult<Boolean> updatePassword(@RequestBody UpdatePasswordRequest request, @AuthenticationPrincipal UserVO user) {
        try {
            boolean result = authService.updatePassword(user.getId(), request.getOldPassword(), request.getNewPassword());
            return BaseResult.success(result);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }
}

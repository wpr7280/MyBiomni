package com.qusu.mybiomni.controller.admin;

import com.qusu.mybiomni.common.annotation.RequireRole;
import com.qusu.mybiomni.common.response.BaseResult;
import com.qusu.mybiomni.controller.auth.AdminVO;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 用户管理 Controller（仅管理员可访问）
 */
@RestController
@RequestMapping("/api/admin/users")
@CrossOrigin(origins = "*")
@RequireRole("admin")  // 类级别注解：整个 Controller 只有管理员可以访问
public class AdminUserController {

    /**
     * 获取用户列表
     * 只有管理员可以访问
     */
    @GetMapping
    public BaseResult<List<Object>> getUserList(@AuthenticationPrincipal AdminVO currentUser) {
        // 业务逻辑
        return BaseResult.success(List.of());
    }

    /**
     * 创建用户
     * 只有管理员可以访问
     */
    @PostMapping
    public BaseResult<Void> createUser(@RequestBody Object request, @AuthenticationPrincipal AdminVO currentUser) {
        // 业务逻辑
        return BaseResult.success(null);
    }

    /**
     * 更新用户
     * 只有管理员可以访问
     */
    @PutMapping("/{id}")
    public BaseResult<Void> updateUser(@PathVariable Integer id, @RequestBody Object request) {
        // 业务逻辑
        return BaseResult.success(null);
    }

    /**
     * 删除用户
     * 只有管理员可以访问
     */
    @DeleteMapping("/{id}")
    public BaseResult<Void> deleteUser(@PathVariable Integer id) {
        // 业务逻辑
        return BaseResult.success(null);
    }
}

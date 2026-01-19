package com.qusu.mybiomni.controller.admin;

import com.qusu.mybiomni.common.annotation.RequireRole;
import com.qusu.mybiomni.common.constant.ResponseEnum;
import com.qusu.mybiomni.common.response.BaseResult;
import com.qusu.mybiomni.common.response.PageResult;
import com.qusu.mybiomni.controller.admin.request.*;
import com.qusu.mybiomni.controller.admin.response.UserVO;
import com.qusu.mybiomni.controller.auth.AdminVO;
import com.qusu.mybiomni.service.UserManagementService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * 用户管理 Controller（仅管理员可访问）
 */
@RestController
@RequestMapping("/api/users")
@CrossOrigin(origins = "*")
@RequireRole("admin")  // 类级别注解：整个 Controller 只有管理员可以访问
public class AdminUserController {

    @Autowired
    private UserManagementService userManagementService;

    /**
     * 获取用户列表（分页）
     */
    @RequestMapping("/list")
    public PageResult<List<UserVO>> getUserList(
            UserListRequest request,
            @AuthenticationPrincipal AdminVO currentUser
    ) {
        try {
            List<UserVO> users = userManagementService.getUserList(request);
            long total = userManagementService.getUserCount(request);
            
            int totalPage = (int) Math.ceil((double) total / request.getPageSize());
            
            return PageResult.success(
                    users,
                    request.getCurrentPage(),
                    request.getPageSize(),
                    totalPage,
                    total
            );
        } catch (Exception e) {
            return PageResult.convertPageResult(ResponseEnum.INTERNAL_SERVER_ERROR);
        }
    }

    /**
     * 创建用户
     */
    @PostMapping("/create")
    public BaseResult<Integer> createUser(
            @Valid @RequestBody CreateUserRequest request,
            @AuthenticationPrincipal AdminVO currentUser
    ) {
        try {
            Integer userId = userManagementService.createUser(request);
            return BaseResult.success(userId);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }

    /**
     * 更新用户
     */
    @PostMapping("/update")
    public BaseResult<Void> updateUser(
            @Valid @RequestBody UpdateUserByIdRequest request
    ) {
        try {
            userManagementService.updateUser(request.getUserId(), request);
            return BaseResult.success(null);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }

    /**
     * 删除用户（软删除）
     */
    @PostMapping("/delete")
    public BaseResult<Void> deleteUser(@Valid @RequestBody DeleteUserRequest request) {
        try {
            userManagementService.deleteUser(request.getUserId());
            return BaseResult.success(null);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }
}

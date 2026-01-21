package com.qusu.mybiomni.service;

import com.qusu.mybiomni.common.constant.AdminStatus;
import com.qusu.mybiomni.common.constant.ForcePasswordChange;
import com.qusu.mybiomni.common.constant.UserRole;
import com.qusu.mybiomni.controller.admin.request.CreateUserRequest;
import com.qusu.mybiomni.controller.admin.request.UpdateUserRequest;
import com.qusu.mybiomni.controller.admin.request.UserListRequest;
import com.qusu.mybiomni.controller.admin.response.UserVO;
import com.qusu.mybiomni.controller.admin.response.QuotaVO;
import com.qusu.mybiomni.dao.mysql.dao.AdminDAO;
import com.qusu.mybiomni.dao.mysql.model.AdminDO;
import com.qusu.mybiomni.dao.mysql.model.AdminDOExample;
import org.apache.ibatis.session.RowBounds;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class UserManagementService {

    @Autowired
    private AdminDAO adminDAO;

    @Autowired
    private AdminService adminService;

    @Autowired
    private PasswordEncoder passwordEncoder;
    
    @Autowired
    private QuotaService quotaService;

    /**
     * 获取用户列表（分页）
     */
    public List<UserVO> getUserList(UserListRequest request) {
        AdminDOExample example = new AdminDOExample();
        AdminDOExample.Criteria criteria = example.createCriteria();

        // 软删除过滤
        criteria.andDeletedAtIsNull();

        // 关键词搜索（用户名或邮箱）
        if (request.getKeyword() != null && !request.getKeyword().trim().isEmpty()) {
            String keyword = "%" + request.getKeyword().trim() + "%";
            AdminDOExample.Criteria orCriteria = example.or();
            orCriteria.andUsernameLike(keyword);
            orCriteria.andDeletedAtIsNull();

            AdminDOExample.Criteria orCriteria2 = example.or();
            orCriteria2.andEmailLike(keyword);
            orCriteria2.andDeletedAtIsNull();
        }

        // 角色筛选
        if (request.getRole() != null && !request.getRole().trim().isEmpty()) {
            criteria.andRoleEqualTo(request.getRole());
        }

        // 状态筛选
        if (request.getStatus() != null) {
            criteria.andStatusEqualTo(request.getStatus());
        }

        // 排序
        example.setOrderByClause("created_at DESC");
        RowBounds rowBounds = new RowBounds(request.getStart(), request.getPageSize());
        // 分页查询
        List<AdminDO> adminList = adminDAO.selectByExampleWithRowbounds(example, rowBounds);

        // 转换为响应对象
        return adminList.stream()
                .skip(request.getStart())
                .limit(request.getPageSize())
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    /**
     * 获取用户总数
     */
    public long getUserCount(UserListRequest request) {
        AdminDOExample example = new AdminDOExample();
        AdminDOExample.Criteria criteria = example.createCriteria();
        criteria.andDeletedAtIsNull();

        if (request.getKeyword() != null && !request.getKeyword().trim().isEmpty()) {
            String keyword = "%" + request.getKeyword().trim() + "%";
            AdminDOExample.Criteria orCriteria = example.or();
            orCriteria.andUsernameLike(keyword);
            orCriteria.andDeletedAtIsNull();

            AdminDOExample.Criteria orCriteria2 = example.or();
            orCriteria2.andEmailLike(keyword);
            orCriteria2.andDeletedAtIsNull();
        }

        if (request.getRole() != null && !request.getRole().trim().isEmpty()) {
            criteria.andRoleEqualTo(request.getRole());
        }

        if (request.getStatus() != null) {
            criteria.andStatusEqualTo(request.getStatus());
        }

        return adminDAO.countByExample(example);
    }

    /**
     * 创建用户
     */
    public Integer createUser(CreateUserRequest request) {
        // 检查邮箱是否已存在
        AdminDO existingUser = adminService.getAdminByEmail(request.getEmail());
        if (existingUser != null) {
            throw new RuntimeException("邮箱已被使用");
        }

        AdminDO admin = new AdminDO();
        admin.setUsername(request.getUsername());
        admin.setEmail(request.getEmail());

        // 密码处理：如果未提供密码，使用默认密码 Password&123
        String password = request.getPassword();
        if (password == null || password.trim().isEmpty()) {
            password = "Password&123";
        }
        admin.setPassword(passwordEncoder.encode(password));

        admin.setRealName(request.getRealName());
        admin.setRole(request.getRole() != null ? request.getRole() : UserRole.USER.getCode());
        admin.setStatus(request.getStatus() != null ? request.getStatus() : AdminStatus.ACTIVE.getCode());
        admin.setLoginFailCount(0);
        admin.setForcePasswordChange(ForcePasswordChange.YES.getCode());  // 首次登录需要修改密码
        admin.setCreatedAt(new Date());
        admin.setUpdatedAt(new Date());

        adminDAO.insert(admin);
        return admin.getId();
    }

    /**
     * 更新用户
     */
    public void updateUser(Integer userId, UpdateUserRequest request) {
        AdminDO existingUser = adminDAO.selectByPrimaryKey(userId);
        if (existingUser == null) {
            throw new RuntimeException("用户不存在");
        }

        // 如果要修改角色，检查是否会导致没有管理员
        if (request.getRole() != null && !request.getRole().trim().isEmpty()) {
            // 如果当前用户是管理员，且要改为普通用户
            if (UserRole.isAdmin(existingUser.getRole()) && !UserRole.isAdmin(request.getRole())) {
                // 检查系统中还有多少个管理员
                long adminCount = countAdmins();
                if (adminCount <= 1) {
                    throw new RuntimeException("系统至少需要保留一名管理员");
                }
            }
        }

        // 如果要禁用用户，检查是否会导致没有可用的管理员
        if (request.getStatus() != null && request.getStatus() == AdminStatus.DISABLED.getCode()) {
            // 如果当前用户是管理员且要禁用
            if (UserRole.isAdmin(existingUser.getRole())) {
                // 检查系统中还有多少个启用的管理员
                long activeAdminCount = countActiveAdmins();
                if (activeAdminCount <= 1) {
                    throw new RuntimeException("系统至少需要保留一名启用的管理员");
                }
            }
        }

        AdminDO updateAdmin = new AdminDO();
        updateAdmin.setId(userId);

        // 更新用户名
        if (request.getUsername() != null && !request.getUsername().trim().isEmpty()) {
            updateAdmin.setUsername(request.getUsername().trim());
        }

        // 更新邮箱
        if (request.getEmail() != null && !request.getEmail().trim().isEmpty()) {
            // 检查邮箱是否被其他用户使用
            AdminDO emailUser = adminService.getAdminByEmail(request.getEmail());
            if (emailUser != null && !emailUser.getId().equals(userId)) {
                throw new RuntimeException("邮箱已被使用");
            }
            updateAdmin.setEmail(request.getEmail().trim());
        }

        // 更新真实姓名
        if (request.getRealName() != null) {
            updateAdmin.setRealName(request.getRealName().trim());
        }

        // 更新角色
        if (request.getRole() != null && !request.getRole().trim().isEmpty()) {
            updateAdmin.setRole(request.getRole());
        }

        // 更新状态
        if (request.getStatus() != null) {
            updateAdmin.setStatus(request.getStatus());
        }

        updateAdmin.setUpdatedAt(new Date());
        adminDAO.updateByPrimaryKeySelective(updateAdmin);

        // 清除缓存
        adminService.evictAdminCache(String.valueOf(userId));
    }

    /**
     * 删除用户（软删除）
     */
    public void deleteUser(Integer userId) {
        AdminDO admin = adminDAO.selectByPrimaryKey(userId);
        if (admin == null) {
            throw new RuntimeException("用户不存在");
        }

        // 如果要删除的是管理员，检查系统中还有多少个管理员
        if (UserRole.isAdmin(admin.getRole())) {
            long adminCount = countAdmins();
            if (adminCount <= 1) {
                throw new RuntimeException("系统至少需要保留一名管理员，无法删除");
            }
        }

        // 软删除
        AdminDO updateAdmin = new AdminDO();
        updateAdmin.setId(userId);
        updateAdmin.setDeletedAt(new Date());
        updateAdmin.setUpdatedAt(new Date());
        adminDAO.updateByPrimaryKeySelective(updateAdmin);

        // 清除缓存
        adminService.evictAdminCache(String.valueOf(userId));
    }

    /**
     * 统计管理员数量
     */
    private long countAdmins() {
        AdminDOExample example = new AdminDOExample();
        example.createCriteria()
                .andRoleEqualTo(UserRole.ADMIN.getCode())
                .andDeletedAtIsNull();
        return adminDAO.countByExample(example);
    }

    /**
     * 统计启用的管理员数量
     */
    private long countActiveAdmins() {
        AdminDOExample example = new AdminDOExample();
        example.createCriteria()
                .andRoleEqualTo(UserRole.ADMIN.getCode())
                .andStatusEqualTo(AdminStatus.ACTIVE.getCode())
                .andDeletedAtIsNull();
        return adminDAO.countByExample(example);
    }

    /**
     * 转换为响应对象
     */
    private UserVO convertToResponse(AdminDO admin) {
        UserVO response = new UserVO();
        BeanUtils.copyProperties(admin, response);
        
        // 添加配额信息
        try {
            QuotaVO quota = quotaService.getUserQuota(admin.getId());
            response.setTotalTokenLimit(quota.getTotalTokenLimit());
            response.setTotalTokenUsed(quota.getTotalTokenUsed());
            response.setRemaining(quota.getRemaining());
            response.setUsagePercent(quota.getUsagePercent());
        } catch (Exception e) {
            // 如果获取配额失败，设置默认值
            response.setTotalTokenLimit(1000000);
            response.setTotalTokenUsed(0);
            response.setRemaining(1000000);
            response.setUsagePercent(0.0);
        }
        
        return response;
    }
}

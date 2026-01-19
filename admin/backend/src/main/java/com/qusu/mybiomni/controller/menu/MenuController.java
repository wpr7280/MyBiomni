package com.qusu.mybiomni.controller.menu;

import com.qusu.mybiomni.common.constant.UserRole;
import com.qusu.mybiomni.common.response.BaseResult;
import com.qusu.mybiomni.common.util.ResultConvert;
import com.qusu.mybiomni.controller.auth.AdminVO;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.ArrayList;
import java.util.List;

@RestController
@RequestMapping("/api/menu")
@CrossOrigin(origins = "*")
public class MenuController {

    /**
     * 管理员菜单
     */
    private static final List<BaseMenu> ADMIN_MENUS;

    /**
     * 普通用户菜单
     */
    private static final List<BaseMenu> USER_MENUS;

    static {
        // ========== 管理员菜单 ==========
        List<BaseMenu> adminMenuList = new ArrayList<>();

//        // 1. 工作台（所有人可见）
//        BaseMenu workbench = menu(1, "工作台", "/workbench", MenuType.MENU,
//                "material-symbols:dashboard-outline", 1, 0,
//                "/workbench", false, true, null);
//        adminMenuList.add(workbench);

        // 2. 对话管理（所有人可见）
        BaseMenu conversations = menu(2, "对话管理", "/conversations", MenuType.MENU,
                "material-symbols:chat-outline", 2, 0,
                "/conversations", false, true, null);
        adminMenuList.add(conversations);

        // 3. Know-How 文档（所有人可见）
        BaseMenu knowhow = menu(3, "知识库", "/knowhow", MenuType.MENU,
                "material-symbols:book-outline", 3, 0,
                "/knowhow", false, true, null);
        adminMenuList.add(knowhow);

        // 4. 系统管理（仅管理员）
        BaseMenu system = menu(10, "系统管理", "/system", MenuType.CATALOG,
                "carbon:gui-management", 10, 0,
                "Layout", false, false, "/system/users");

        system.setChildren(List.of(
                child(11, "用户管理", "users", 1, system, "material-symbols:person-outline", "/system/users"),
                child(12, "配额管理", "quota", 2, system, "material-symbols:data-usage-outline", "/system/quota"),
                child(13, "对话记录", "conversations-admin", 3, system, "material-symbols:history", "/system/conversations"),
                child(14, "文档管理", "knowhow-admin", 4, system, "material-symbols:library-books-outline", "/system/knowhow")
        ));
        adminMenuList.add(system);

        // 5. 系统配置（仅管理员）
        BaseMenu config = menu(20, "系统配置", "/config", MenuType.CATALOG,
                "material-symbols:settings-outline", 20, 0,
                "Layout", false, false, "/config/model");

        config.setChildren(List.of(
                child(21, "模型配置", "model", 1, config, "material-symbols:psychology-outline", "/config/model"),
                child(22, "商用模式", "commercial", 2, config, "material-symbols:business-center-outline", "/config/commercial"),
                child(23, "系统设置", "system", 3, config, "material-symbols:tune-outline", "/config/system")
        ));
        adminMenuList.add(config);

        ADMIN_MENUS = adminMenuList;

        // ========== 普通用户菜单 ==========
        List<BaseMenu> userMenuList = new ArrayList<>();

        // 1. 工作台
        userMenuList.add(menu(1, "工作台", "/workbench", MenuType.MENU,
                "material-symbols:dashboard-outline", 1, 0,
                "/workbench", false, true, null));

        // 2. 我的对话
        userMenuList.add(menu(2, "我的对话", "/conversations", MenuType.MENU,
                "material-symbols:chat-outline", 2, 0,
                "/conversations", false, true, null));

        // 3. 知识库
        userMenuList.add(menu(3, "知识库", "/knowhow", MenuType.MENU,
                "material-symbols:book-outline", 3, 0,
                "/knowhow", false, true, null));

        USER_MENUS = userMenuList;
    }

    /**
     * 构造父目录或顶级菜单
     */
    private static BaseMenu menu(Integer id, String name, String path, MenuType type,
                                 String icon, Integer order, Integer parentId,
                                 String component, boolean hidden, boolean keepalive, String redirect) {
        BaseMenu m = new BaseMenu();
        m.setId(id);
        m.setName(name);
        m.setPath(path);
        m.setMenuType(type);
        m.setIcon(icon);
        m.setOrder(order);
        m.setParentId(parentId);
        m.setIsHidden(hidden);
        m.setComponent(component);
        m.setKeepalive(keepalive);
        m.setRedirect(redirect);
        return m;
    }

    /**
     * 构造子菜单
     */
    private static BaseMenu child(Integer id, String name, String path, Integer order, BaseMenu parent,
                                  String icon, String component) {
        return menu(id, name, path, MenuType.MENU,
                icon, order, parent.getId(), component, false, false, null);
    }

    /**
     * 获取用户菜单
     * 根据用户角色返回不同的菜单
     */
    @PreAuthorize("isAuthenticated()")
    @RequestMapping("/list")
    public BaseResult<List<BaseMenu>> getUserMenu(@AuthenticationPrincipal AdminVO currentUser) {
        // 根据角色返回不同菜单
        if (UserRole.isAdmin(currentUser.getRole())) {
            // 管理员返回完整菜单
            return ResultConvert.initSuccess(ADMIN_MENUS);
        } else {
            // 普通用户返回基础菜单
            return ResultConvert.initSuccess(USER_MENUS);
        }
    }
}

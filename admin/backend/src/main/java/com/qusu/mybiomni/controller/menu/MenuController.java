package com.qusu.mybiomni.controller.menu;

import com.qusu.mybiomni.common.response.BaseResult;
import com.qusu.mybiomni.common.util.ResultConvert;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/menu")
@CrossOrigin(origins = "*")
public class MenuController {
    private static final List<BaseMenu> ADMIN_MENUS;

    static {
        // 父目录：系统管理
        BaseMenu sys = menu(1, "功能", "/system", MenuType.CATALOG,
                "carbon:gui-management", 1, 0,
                "Layout", false, false, "/system/user");

        sys.setChildren(List.of(
                child(2, "沙箱管理", "sandboxs", 1, sys, "material-symbols:person-outline-rounded", "/system/sandboxs"),
                child(3, "模版管理", "templates", 2, sys, "carbon:user-role", "/system/templates"),
                child(4, "用量", "usage", 3, sys, "material-symbols:list-alt-outline", "/system/usage")
        ));

        BaseMenu team = menu(8, "团队", "/members", MenuType.MENU,
                "material-symbols:featured-play-list-outline", 2, 0,
                "/teams", false, false, null);
        team.setChildren(
                List.of(
                        child(9, "团队管理", "teams", 1, team, "material-symbols:person-outline-rounded", "/members/teams"),
                        child(10, "APIKeys", "apikey", 1, team, "material-symbols:person-outline-rounded", "/members/apikey")
                )
        );
        ADMIN_MENUS = List.of(sys, team);
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
        BaseMenu c = menu(id, name, path, MenuType.MENU,
                icon, order, parent.getId(), component, false, false, null);
        return c;
    }

    @PreAuthorize("isAuthenticated()")
    @RequestMapping("/list")
    public BaseResult<List<BaseMenu>> getUsermenu() {
        return ResultConvert.initSuccess(ADMIN_MENUS);
    }

}

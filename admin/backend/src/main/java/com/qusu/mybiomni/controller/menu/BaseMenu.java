package com.qusu.mybiomni.controller.menu;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Data;

import java.util.List;
import java.util.Map;

@Data
@JsonInclude(JsonInclude.Include.NON_NULL)
public class BaseMenu {
    /** 主键 */
    private Integer id;

    /** 菜单名称 */
    private String name;

    /** 前端路由 path */
    private String path;

    /** 备注，任意 JSON 对象 */
    private Map<String, Object> remark;

    /** 菜单类型（目录 / 菜单） */
    private MenuType menuType;

    /** 图标 */
    private String icon;

    /** 排序值 */
    private Integer order;

    /** 父级菜单 ID */
    private Integer parentId;

    /** 是否在侧边栏隐藏 */
    private Boolean isHidden;

    /** Vue 组件路径 */
    private String component;

    /** 页面是否 keep-alive */
    private Boolean keepalive;

    /** 重定向路由，可空 */
    private String redirect;

    /** 子菜单 */
    private List<BaseMenu> children;
}

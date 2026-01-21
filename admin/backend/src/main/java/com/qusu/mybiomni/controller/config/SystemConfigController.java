package com.qusu.mybiomni.controller.config;

import com.qusu.mybiomni.common.annotation.RequireRole;
import com.qusu.mybiomni.common.response.BaseResult;
import com.qusu.mybiomni.controller.config.request.BatchUpdateConfigRequest;
import com.qusu.mybiomni.controller.config.request.UpdateConfigRequest;
import com.qusu.mybiomni.controller.config.response.SystemConfigVO;
import com.qusu.mybiomni.service.SystemConfigService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * 系统配置 Controller（仅管理员可访问）
 */
@RestController
@RequestMapping("/api/config")
@CrossOrigin(origins = "*")
@RequireRole("admin")
public class SystemConfigController {
    
    @Autowired
    private SystemConfigService systemConfigService;
    
    /**
     * 获取 Agent 配置列表
     */
    @PostMapping("/list")
    public BaseResult<List<SystemConfigVO>> getConfigList() {
        try {
            List<SystemConfigVO> configs = systemConfigService.getAgentConfigs();
            return BaseResult.success(configs);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }
    
    /**
     * 更新单个配置
     */
    @PostMapping("/update")
    public BaseResult<Void> updateConfig(@Valid @RequestBody UpdateConfigRequest request) {
        try {
            systemConfigService.updateConfig(request.getConfigKey(), request.getConfigValue());
            return BaseResult.success(null);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }
    
    /**
     * 批量更新配置
     */
    @PostMapping("/batch-update")
    public BaseResult<Void> batchUpdateConfigs(@Valid @RequestBody BatchUpdateConfigRequest request) {
        try {
            systemConfigService.batchUpdateConfigs(request.getConfigs());
            return BaseResult.success(null);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }
    
    /**
     * 重置为默认值
     */
    @PostMapping("/reset")
    public BaseResult<Void> resetToDefault() {
        try {
            systemConfigService.resetToDefault();
            return BaseResult.success(null);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }
    
    /**
     * 检查配置状态
     */
    @PostMapping("/status")
    public BaseResult<ConfigStatusVO> getConfigStatus() {
        try {
            ConfigStatusVO status = systemConfigService.getConfigStatus();
            return BaseResult.success(status);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }
    
    /**
     * 获取完整配置（不脱敏，仅管理员）
     */
    @PostMapping("/list-full")
    public BaseResult<List<SystemConfigVO>> getConfigListFull() {
        try {
            List<SystemConfigVO> configs = systemConfigService.getAgentConfigsFull();
            return BaseResult.success(configs);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }

    /**
     * 配置状态 VO
     */
    @lombok.Data
    public static class ConfigStatusVO {
        private Boolean isConfigured;  // 是否已配置
        private Boolean hasApiKey;     // 是否配置了 API Key
        private String currentSource;  // 当前提供商
        private String message;        // 提示信息
    }
}

package com.qusu.mybiomni.service;

import com.qusu.mybiomni.controller.config.SystemConfigController;
import com.qusu.mybiomni.controller.config.response.SystemConfigVO;
import com.qusu.mybiomni.dao.mysql.dao.SystemConfigDAO;
import com.qusu.mybiomni.dao.mysql.model.SystemConfigDO;
import com.qusu.mybiomni.dao.mysql.model.SystemConfigDOExample;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 系统配置服务
 */
@Service
public class SystemConfigService {
    
    @Autowired
    private SystemConfigDAO systemConfigDAO;
    
    /**
     * 获取所有 Agent 配置
     */
    public List<SystemConfigVO> getAgentConfigs() {
        SystemConfigDOExample example = new SystemConfigDOExample();
        example.createCriteria().andConfigKeyLike("agent.%");
        
        SystemConfigDOExample example2 = new SystemConfigDOExample();
        example2.or().andConfigKeyLike("llm.%");
        
        example.or(example2.getOredCriteria().get(0));
        example.setOrderByClause("config_key ASC");
        
        List<SystemConfigDO> configs = systemConfigDAO.selectByExample(example);
        
        return configs.stream()
                .map(this::convertToVO)
                .collect(Collectors.toList());
    }
    
    /**
     * 获取所有 Agent 配置（完整版，不脱敏）
     */
    public List<SystemConfigVO> getAgentConfigsFull() {
        return getAgentConfigs();  // 直接返回，不脱敏
    }
    /**
     * 获取单个配置
     */
    public SystemConfigVO getConfig(String configKey) {
        SystemConfigDOExample example = new SystemConfigDOExample();
        example.createCriteria().andConfigKeyEqualTo(configKey);
        
        List<SystemConfigDO> configs = systemConfigDAO.selectByExample(example);
        
        if (configs.isEmpty()) {
            return null;
        }
        
        return convertToVO(configs.get(0));
    }
    
    /**
     * 更新配置
     */
    @Transactional
    public void updateConfig(String configKey, String configValue) {
        // 验证配置值
        validateConfigValue(configKey, configValue);
        
        SystemConfigDOExample example = new SystemConfigDOExample();
        example.createCriteria().andConfigKeyEqualTo(configKey);
        
        List<SystemConfigDO> configs = systemConfigDAO.selectByExample(example);
        
        if (configs.isEmpty()) {
            // 配置不存在，自动创建
            SystemConfigDO newConfig = new SystemConfigDO();
            newConfig.setConfigKey(configKey);
            newConfig.setConfigValue(configValue);
            
            // 根据 key 设置类型和描述
            if (configKey.contains("temperature")) {
                newConfig.setConfigType("float");
                newConfig.setDescription("Temperature");
            } else if (configKey.contains("timeout")) {
                newConfig.setConfigType("int");
                newConfig.setDescription("Timeout");
            } else if (configKey.contains("use_") || configKey.contains("_mode")) {
                newConfig.setConfigType("bool");
                newConfig.setDescription("Toggle");
            } else {
                newConfig.setConfigType("string");
                newConfig.setDescription("Config");
            }
            
            // API Key 标记为敏感
            if (configKey.contains("key") || configKey.contains("secret") || configKey.contains("token")) {
                newConfig.setIsSensitive(1);
            } else {
                newConfig.setIsSensitive(0);
            }
            
            newConfig.setCreatedAt(new Date());
            newConfig.setUpdatedAt(new Date());
            systemConfigDAO.insert(newConfig);
            
            System.out.println("Auto-created config: " + configKey + " = " + configValue);
        } else {
            // 配置存在，更新
            SystemConfigDO config = configs.get(0);
            config.setConfigValue(configValue);
            config.setUpdatedAt(new Date());
            systemConfigDAO.updateByPrimaryKeySelective(config);
        }
    }
    
    /**
     * 批量更新配置
     */
    @Transactional
    public void batchUpdateConfigs(Map<String, String> configs) {
        for (Map.Entry<String, String> entry : configs.entrySet()) {
            updateConfig(entry.getKey(), entry.getValue());
        }
    }
    
    /**
     * 重置为默认值
     */
    @Transactional
    public void resetToDefault() {
        Map<String, String> defaults = Map.of(
            "agent.llm", "claude-sonnet-4-5",
            "agent.source", "Anthropic",
            "agent.temperature", "0.7",
            "agent.timeout_seconds", "600",
            "agent.use_tool_retriever", "true",
            "agent.commercial_mode", "false",
            "agent.base_url", "",
            "agent.api_key", ""
        );
        
        batchUpdateConfigs(defaults);
    }
    
    /**
     * 获取配置状态
     */
    public SystemConfigController.ConfigStatusVO getConfigStatus() {
        SystemConfigController.ConfigStatusVO status = new SystemConfigController.ConfigStatusVO();
        
        // 检查是否有配置记录
        List<SystemConfigVO> configs = getAgentConfigs();
        
        if (configs.isEmpty()) {
            status.setIsConfigured(false);
            status.setHasApiKey(false);
            status.setCurrentSource(null);
            status.setMessage("System not configured. Please initialize configuration first.");
            return status;
        }
        
        status.setIsConfigured(true);
        
        // 获取当前提供商
        SystemConfigVO sourceConfig = getConfig("agent.source");
        String source = sourceConfig != null ? sourceConfig.getConfigValue() : "Anthropic";
        status.setCurrentSource(source);
        
        // 检查是否配置了对应的 API Key
        boolean hasApiKey = false;
        
        switch (source) {
            case "OpenAI":
                hasApiKey = hasValidApiKey("llm.openai_api_key");
                break;
            case "Anthropic":
                hasApiKey = hasValidApiKey("llm.anthropic_api_key");
                break;
            case "Gemini":
                hasApiKey = hasValidApiKey("llm.gemini_api_key");
                break;
            case "Groq":
                hasApiKey = hasValidApiKey("llm.groq_api_key");
                break;
            case "AzureOpenAI":
                hasApiKey = hasValidApiKey("llm.azure_api_key") && hasValidApiKey("llm.azure_endpoint");
                break;
            case "Bedrock":
                // Bedrock 支持两种认证方式：
                // 1. Access Key + Secret Key
                // 2. Bearer Token
                boolean hasAccessKey = hasValidApiKey("llm.aws_access_key_id") && hasValidApiKey("llm.aws_secret_access_key");
                boolean hasBearerToken = hasValidApiKey("llm.aws_bearer_token");
                hasApiKey = hasAccessKey || hasBearerToken;
                break;
            case "Ollama":
                hasApiKey = true;  // Ollama 不需要 API Key
                break;
            case "Custom":
                hasApiKey = hasValidApiKey("agent.base_url") && hasValidApiKey("agent.api_key");
                break;
        }
        
        status.setHasApiKey(hasApiKey);
        
        if (!hasApiKey) {
            status.setMessage("Please configure the API Key for " + source + " before use.");
        } else {
            status.setMessage("Configuration OK");
        }
        
        return status;
    }
    
    /**
     * 检查是否有有效的 API Key
     */
    private boolean hasValidApiKey(String configKey) {
        SystemConfigVO config = getConfig(configKey);
        return config != null && config.getConfigValue() != null && !config.getConfigValue().trim().isEmpty();
    }
    
    /**
     * 验证配置值
     */
    private void validateConfigValue(String configKey, String configValue) {
        switch (configKey) {
            case "agent.source":
                List<String> validSources = List.of("OpenAI", "AzureOpenAI", "Anthropic", "Ollama", "Gemini", "Groq", "Bedrock", "Custom");
                if (!validSources.contains(configValue)) {
                    throw new RuntimeException("Invalid LLM provider: " + configValue);
                }
                break;
            
            case "agent.temperature":
                try {
                    float temp = Float.parseFloat(configValue);
                    if (temp < 0 || temp > 2) {
                        throw new RuntimeException("Temperature must be between 0 and 2");
                    }
                } catch (NumberFormatException e) {
                    throw new RuntimeException("Temperature must be a number");
                }
                break;
            
            case "agent.timeout_seconds":
                try {
                    int timeout = Integer.parseInt(configValue);
                    if (timeout < 60 || timeout > 3600) {
                        throw new RuntimeException("Timeout must be between 60 and 3600 seconds");
                    }
                } catch (NumberFormatException e) {
                    throw new RuntimeException("Timeout must be an integer");
                }
                break;
            
            case "agent.use_tool_retriever":
            case "agent.commercial_mode":
                if (!configValue.equals("true") && !configValue.equals("false")) {
                    throw new RuntimeException("Value must be true or false");
                }
                break;
        }
    }
    
    /**
     * 转换为 VO（不脱敏，直接返回原始值）
     */
    private SystemConfigVO convertToVO(SystemConfigDO config) {
        SystemConfigVO vo = new SystemConfigVO();
        BeanUtils.copyProperties(config, vo);
        return vo;
    }
}

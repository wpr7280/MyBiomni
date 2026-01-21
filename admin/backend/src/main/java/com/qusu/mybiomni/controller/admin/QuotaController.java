package com.qusu.mybiomni.controller.admin;

import com.qusu.mybiomni.common.annotation.RequireRole;
import com.qusu.mybiomni.common.response.BaseResult;
import com.qusu.mybiomni.controller.admin.request.ResetQuotaRequest;
import com.qusu.mybiomni.controller.admin.request.UpdateQuotaRequest;
import com.qusu.mybiomni.controller.admin.response.QuotaVO;
import com.qusu.mybiomni.service.QuotaService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;

/**
 * 配额管理 Controller（仅管理员可访问）
 */
@RestController
@RequestMapping("/api/quota")
@CrossOrigin(origins = "*")
@RequireRole("admin")
public class QuotaController {
    
    @Autowired
    private QuotaService quotaService;
    
    /**
     * 获取用户配额
     */
    @PostMapping("/get")
    public BaseResult<QuotaVO> getQuota(@RequestBody GetQuotaRequest request) {
        try {
            QuotaVO quota = quotaService.getUserQuota(request.getUserId());
            return BaseResult.success(quota);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }
    
    /**
     * 更新用户配额
     */
    @PostMapping("/update")
    public BaseResult<Void> updateQuota(@Valid @RequestBody UpdateQuotaRequest request) {
        try {
            quotaService.updateQuota(request.getUserId(), request.getTotalTokenLimit());
            return BaseResult.success(null);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }
    
    /**
     * 重置用户配额使用量
     */
    @PostMapping("/reset")
    public BaseResult<Void> resetQuota(@Valid @RequestBody ResetQuotaRequest request) {
        try {
            quotaService.resetQuota(request.getUserId());
            return BaseResult.success(null);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }
    
    /**
     * 获取配额请求
     */
    @lombok.Data
    public static class GetQuotaRequest {
        @javax.validation.constraints.NotNull(message = "用户ID不能为空")
        private Integer userId;
    }
}

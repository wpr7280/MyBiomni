package com.qusu.mybiomni.controller.admin;

import com.qusu.mybiomni.common.annotation.RequireRole;
import com.qusu.mybiomni.common.constant.ResponseEnum;
import com.qusu.mybiomni.common.response.BaseResult;
import com.qusu.mybiomni.common.response.PageResult;
import com.qusu.mybiomni.controller.admin.request.AdminConversationListRequest;
import com.qusu.mybiomni.controller.admin.request.DeleteConversationRequest;
import com.qusu.mybiomni.controller.admin.response.AdminConversationVO;
import com.qusu.mybiomni.controller.auth.AdminVO;
import com.qusu.mybiomni.service.AdminConversationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * 管理员对话管理 Controller（仅管理员可访问）
 */
@RestController
@RequestMapping("/api/admin/conversations")
@CrossOrigin(origins = "*")
@RequireRole("admin")
public class AdminConversationController {
    
    @Autowired
    private AdminConversationService adminConversationService;
    
    /**
     * 获取对话列表（管理员视图）
     */
    @PostMapping("/list")
    public PageResult<List<AdminConversationVO>> getConversationList(
            @RequestBody AdminConversationListRequest request,
            @AuthenticationPrincipal AdminVO currentUser
    ) {
        try {
            List<AdminConversationVO> conversations = adminConversationService.getConversationList(request);
            long total = adminConversationService.getConversationCount(request);
            
            int totalPage = (int) Math.ceil((double) total / request.getPageSize());
            
            return PageResult.success(
                    conversations,
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
     * 删除对话（管理员操作）
     */
    @PostMapping("/delete")
    public BaseResult<Void> deleteConversation(
            @Valid @RequestBody DeleteConversationRequest request,
            @AuthenticationPrincipal AdminVO currentUser
    ) {
        try {
            adminConversationService.deleteConversation(request.getConversationId());
            return BaseResult.success(null);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }
}

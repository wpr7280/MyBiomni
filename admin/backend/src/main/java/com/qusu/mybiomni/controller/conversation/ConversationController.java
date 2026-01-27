package com.qusu.mybiomni.controller.conversation;

import com.qusu.mybiomni.common.constant.ResponseEnum;
import com.qusu.mybiomni.common.request.PageRequest;
import com.qusu.mybiomni.common.response.BaseResult;
import com.qusu.mybiomni.common.response.PageResult;
import com.qusu.mybiomni.controller.auth.AdminVO;
import com.qusu.mybiomni.controller.conversation.request.*;
import com.qusu.mybiomni.controller.conversation.response.ConversationVO;
import com.qusu.mybiomni.service.ConversationExportService;
import com.qusu.mybiomni.service.ConversationService;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * 对话管理 Controller
 */
@Slf4j
@RestController
@RequestMapping("/api/conversations")
@CrossOrigin(origins = "*")
public class ConversationController {

    @Autowired
    private ConversationService conversationService;

    @Autowired
    private ConversationExportService conversationExportService;

    /**
     * 获取对话列表（分页）
     */
    @RequestMapping("/list")
    public PageResult<List<ConversationVO>> getConversations(
            PageRequest pageRequest,
            @AuthenticationPrincipal AdminVO currentUser) {
        try {
            List<ConversationVO> conversations = conversationService.getConversationList(
                    currentUser.getId(), pageRequest);
            long total = conversationService.getConversationCount(currentUser.getId());
            int totalPage = (int) Math.ceil((double) total / pageRequest.getPageSize());

            return PageResult.success(conversations, pageRequest.getCurrentPage(),
                    pageRequest.getPageSize(), totalPage , total);
        } catch (Exception e) {
            return PageResult.convertPageResult(ResponseEnum.INTERNAL_SERVER_ERROR);
        }
    }

    /**
     * 创建新对话
     */
    @PostMapping("/create")
    public BaseResult<ConversationVO> createConversation(
            @Valid @RequestBody CreateConversationRequest request,
            @AuthenticationPrincipal AdminVO currentUser) {
        try {
            ConversationVO conversation = conversationService.createConversation(
                    currentUser.getId(), request.getTitle()
            );
            return BaseResult.success(conversation);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }

    /**
     * 获取对话详情
     */
    @RequestMapping("/get")
    public BaseResult<ConversationVO> getConversation(
            @Valid @RequestBody GetConversationRequest request,
            @AuthenticationPrincipal AdminVO currentUser) {
        try {
            ConversationVO conversation = conversationService.getConversation(
                    request.getConversationId(), currentUser.getId()
            );
            return BaseResult.success(conversation);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }

    /**
     * 更新对话标题（重命名）
     */
    @PostMapping("/update")
    public BaseResult<Void> updateConversation(
            @Valid @RequestBody UpdateConversationTitleRequest request,
            @AuthenticationPrincipal AdminVO currentUser) {
        try {
            conversationService.updateConversation(
                    request.getConversationId(), 
                    currentUser.getId(), 
                    request.getTitle()
            );
            return BaseResult.success(null);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }

    /**
     * 删除对话（软删除）
     */
    @PostMapping("/delete")
    public BaseResult<Void> deleteConversation(
            @Valid @RequestBody DeleteConversationRequest request,
            @AuthenticationPrincipal AdminVO currentUser) {
        try {
            conversationService.deleteConversation(
                    request.getConversationId(), currentUser.getId()
            );
            return BaseResult.success(null);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }

    /**
     * 导出对话为 Markdown
     */
    @PostMapping("/export")
    public void exportConversation(
            @Valid @RequestBody ExportConversationRequest request,
            @AuthenticationPrincipal AdminVO currentUser,
            HttpServletResponse response) {
        try {
            // 导出为 Markdown（可能打包为 ZIP）
            ConversationExportService.ExportResult result = conversationExportService.exportConversationToMarkdown(
                    request.getConversationId(),
                    currentUser.getId(),
                    currentUser.isAdmin(),
                    request.getIncludeImages() != null ? request.getIncludeImages() : true
            );

            // 读取文件并返回
            java.io.File file = conversationExportService.getExportFile(result.getFilepath());
            
            // 根据文件类型设置 Content-Type
            if (result.isZip()) {
                response.setContentType("application/zip");
            } else {
                response.setContentType("text/markdown");
            }
            
            response.setHeader("Content-Disposition", 
                "attachment; filename=\"" + file.getName() + "\"");
            response.setContentLengthLong(file.length());

            try (java.io.FileInputStream fis = new java.io.FileInputStream(file);
                 java.io.OutputStream os = response.getOutputStream()) {
                byte[] buffer = new byte[8192];
                int bytesRead;
                while ((bytesRead = fis.read(buffer)) != -1) {
                    os.write(buffer, 0, bytesRead);
                }
                os.flush();
            }

            // 导出后删除临时文件
//            file.delete();
            
            log.info("对话导出成功: conversationId={}, userId={}, role={}, isZip={}, images={}", 
                request.getConversationId(), currentUser.getId(), currentUser.getRole(), 
                result.isZip(), result.getImageCount());
            
        } catch (IllegalArgumentException e) {
            log.warn("导出对话权限不足: conversationId={}, userId={}, role={}, error={}", 
                request.getConversationId(), currentUser.getId(), currentUser.getRole(), e.getMessage());
            response.setStatus(HttpServletResponse.SC_FORBIDDEN);
            try {
                response.getWriter().write("{\"error\": \"" + e.getMessage() + "\"}");
            } catch (Exception ex) {
                log.error("写入错误响应失败", ex);
            }
        } catch (Exception e) {
            log.error("导出对话失败: conversationId={}, userId={}", 
                request.getConversationId(), currentUser.getId(), e);
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            try {
                response.getWriter().write("{\"error\": \"导出失败\"}");
            } catch (Exception ex) {
                log.error("写入错误响应失败", ex);
            }
        }
    }
}

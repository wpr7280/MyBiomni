package com.qusu.mybiomni.controller.conversation;

import com.qusu.mybiomni.common.constant.ResponseEnum;
import com.qusu.mybiomni.common.request.PageRequest;
import com.qusu.mybiomni.common.response.BaseResult;
import com.qusu.mybiomni.common.response.PageResult;
import com.qusu.mybiomni.controller.auth.AdminVO;
import com.qusu.mybiomni.controller.conversation.request.*;
import com.qusu.mybiomni.controller.conversation.response.ConversationVO;
import com.qusu.mybiomni.service.ConversationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * 对话管理 Controller
 */
@RestController
@RequestMapping("/api/conversations")
@CrossOrigin(origins = "*")
public class ConversationController {

    @Autowired
    private ConversationService conversationService;

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
}

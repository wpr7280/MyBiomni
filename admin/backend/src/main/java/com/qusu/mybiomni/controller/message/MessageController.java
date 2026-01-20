package com.qusu.mybiomni.controller.message;

import com.qusu.mybiomni.common.constant.ResponseEnum;
import com.qusu.mybiomni.common.response.BaseResult;
import com.qusu.mybiomni.common.response.PageResult;
import com.qusu.mybiomni.controller.auth.AdminVO;
import com.qusu.mybiomni.controller.message.request.*;
import com.qusu.mybiomni.controller.message.response.MessageVO;
import com.qusu.mybiomni.service.MessageService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * 消息管理 Controller
 */
@RestController
@RequestMapping("/api/messages")
@CrossOrigin(origins = "*")
public class MessageController {

    @Autowired
    private MessageService messageService;

    /**
     * 获取对话的消息列表（分页）
     */
    @RequestMapping("/list")
    public PageResult<List<MessageVO>> getMessages(
            GetMessagesRequest request,
            @AuthenticationPrincipal AdminVO currentUser) {
        try {
            List<MessageVO> messages = messageService.getMessageList(
                    request.getConversationId(), 
                    currentUser.getId(),
                    request
            );
            long total = messageService.getMessageCount(request.getConversationId());
            
            int totalPage = (int) Math.ceil((double) total / request.getPageSize());
            
            return PageResult.success(
                    messages, 
                    request.getCurrentPage(), 
                    request.getPageSize(), 
                    totalPage, 
                    total
            );
        } catch (Exception e) {
            return PageResult.convertPageResult(ResponseEnum.INTERNAL_SERVER_ERROR);
        }
    }

//    /**
//     * 发送消息
//     */
//    @PostMapping("/send")
//    public BaseResult<MessageVO> sendMessage(
//            @Valid @RequestBody SendMessageRequest request,
//            @AuthenticationPrincipal AdminVO currentUser) {
//        try {
//            MessageVO message = messageService.sendMessage(
//                    request.getConversationId(),
//                    currentUser.getId(),
//                    request.getContent()
//            );
//            return BaseResult.success(message);
//        } catch (Exception e) {
//            return BaseResult.error(e.getMessage());
//        }
//    }
}

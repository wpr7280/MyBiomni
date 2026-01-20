package com.qusu.mybiomni.controller.execution;

import com.qusu.mybiomni.common.response.BaseResult;
import com.qusu.mybiomni.controller.auth.AdminVO;
import com.qusu.mybiomni.controller.execution.response.ExecutionStepVO;
import com.qusu.mybiomni.service.ExecutionStepService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 执行步骤 Controller
 */
@RestController
@RequestMapping("/api/execution-steps")
@CrossOrigin(origins = "*")
public class ExecutionStepController {

    @Autowired
    private ExecutionStepService executionStepService;

    /**
     * 获取消息的执行步骤
     */
    @RequestMapping("/list")
    public BaseResult<List<ExecutionStepVO>> getExecutionSteps(
            @RequestParam Integer messageId,
            @AuthenticationPrincipal AdminVO currentUser
    ) {
        try {
            List<ExecutionStepVO> steps = executionStepService.getExecutionSteps(messageId);
            return BaseResult.success(steps);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }
}

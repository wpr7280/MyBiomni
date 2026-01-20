package com.qusu.mybiomni.service;

import com.qusu.mybiomni.controller.execution.response.ExecutionStepVO;
import com.qusu.mybiomni.dao.mysql.dao.ExecutionStepDAO;
import com.qusu.mybiomni.dao.mysql.model.ExecutionStepDO;
import com.qusu.mybiomni.dao.mysql.model.ExecutionStepDOExample;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class ExecutionStepService {

    @Autowired
    private ExecutionStepDAO executionStepDAO;

    /**
     * 获取消息的执行步骤
     */
    public List<ExecutionStepVO> getExecutionSteps(Integer messageId) {
        ExecutionStepDOExample example = new ExecutionStepDOExample();
        example.createCriteria().andMessageIdEqualTo(messageId);
        example.setOrderByClause("step_order ASC");
        
        List<ExecutionStepDO> steps = executionStepDAO.selectByExample(example);
        
        return steps.stream()
                .map(this::convertToVO)
                .collect(Collectors.toList());
    }

    /**
     * 转换为 VO
     */
    private ExecutionStepVO convertToVO(ExecutionStepDO step) {
        ExecutionStepVO vo = new ExecutionStepVO();
        BeanUtils.copyProperties(step, vo);
        return vo;
    }
}

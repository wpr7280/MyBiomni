package com.qusu.mybiomni.controller.execution.response;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class ExecutionStepVO {
    private Integer id;
    private Integer conversationId;
    private Integer messageId;
    private Integer stepOrder;
    private String stepType;
    private String stepName;
    private String toolName;
    private String toolInput;
    private String toolOutput;
    private String status;
    private String errorMessage;
    private Integer durationMs;
    private LocalDateTime startedAt;
    private LocalDateTime completedAt;
}

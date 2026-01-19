package com.qusu.mybiomni.common.interceptor;

import com.qusu.mybiomni.common.constant.ResponseEnum;
import com.qusu.mybiomni.common.exception.BusinessException;
import com.qusu.mybiomni.common.response.BaseResult;
import com.qusu.mybiomni.common.util.ResultConvert;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import javax.validation.ConstraintViolationException;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {
    /**
     * 业务异常（主动抛出的）
     */
    @ExceptionHandler(BusinessException.class)
    public BaseResult<?> handleBusinessException(BusinessException ex) {
        log.warn("[业务异常] {}", ex.getMessage());
        return ResultConvert.convertResult(ex.getCode(), ex.getMessage());
    }

    /**
     * 参数验证失败（@Validated + @RequestBody）
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public BaseResult<?> handleValidException(MethodArgumentNotValidException ex) {
        String msg = ex.getBindingResult().getFieldError().getDefaultMessage();
        log.warn("[参数校验异常] {}", msg);
        return ResultConvert.convertResult(ResponseEnum.ILLEGAL_PARAMETER.getCode(), msg);
    }

    /**
     * 单个参数验证失败（如 @RequestParam）
     */
    @ExceptionHandler(ConstraintViolationException.class)
    public BaseResult<?> handleConstraintViolation(ConstraintViolationException ex) {
        String msg = ex.getConstraintViolations().iterator().next().getMessage();
        log.warn("[约束校验异常] {}", msg);
        return ResultConvert.convertResult(ResponseEnum.ILLEGAL_PARAMETER.getCode(), msg);
    }

    /**
     * 未知异常（兜底）
     */
    @ExceptionHandler(Exception.class)
    public BaseResult<?> handleException(Exception ex) {
        log.error("[系统异常]", ex);
        return ResultConvert.convertResult(ResponseEnum.INTERNAL_SERVER_ERROR.getCode(), ResponseEnum.INTERNAL_SERVER_ERROR.getMsg());
    }
}

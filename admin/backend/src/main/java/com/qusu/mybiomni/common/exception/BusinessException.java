package com.qusu.mybiomni.common.exception;

import com.qusu.mybiomni.common.constant.ResponseEnum;
import lombok.Getter;

@Getter
public class BusinessException extends RuntimeException {
    private final int code;

    public BusinessException(ResponseEnum responseEnum) {
        super(responseEnum.getMsg());
        this.code = responseEnum.getCode();
    }
}
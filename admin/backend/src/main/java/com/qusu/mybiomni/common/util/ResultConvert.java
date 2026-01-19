package com.qusu.mybiomni.common.util;


import com.qusu.mybiomni.common.constant.ResponseEnum;
import com.qusu.mybiomni.common.response.BaseResult;

public class ResultConvert {
    public static <T> BaseResult<T> initSuccess(T t) {
        return convertResult(ResponseEnum.SUCCESS, t);
    }

    public static <T> BaseResult<T> convertResult(ResponseEnum response, T t) {
        BaseResult<T> result = new BaseResult<>();
        result.setCode(response.getCode());
        result.setMsg(response.getMsg());
        result.setData(t);
        return result;
    }

    public static <T> BaseResult<T> convertResult(ResponseEnum response) {
        return convertResult(response.getCode(), response.getMsg());
    }

    public static <T> BaseResult<T> convertResult(int code, String msg) {
        BaseResult<T> result = new BaseResult<>();
        result.setCode(code);
        result.setMsg(msg);
        return result;
    }


}

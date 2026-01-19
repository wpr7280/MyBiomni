package com.qusu.mybiomni.common.response;

public class BaseResult<T> {
    private int code;
    private String msg;
    private T data;

    public BaseResult() {}

    public BaseResult(int code, String msg, T data) {
        this.code = code;
        this.msg = msg;
        this.data = data;
    }

    public static <T> BaseResult<T> success(T data) {
        return new BaseResult<>(200, "success", data);
    }

    public static <T> BaseResult<T> error(String message) {
        return new BaseResult<>(500, message, null);
    }

    public static <T> BaseResult<T> error(int code, String message) {
        return new BaseResult<>(code, message, null);
    }

    // getters and setters
    public int getCode() { return code; }
    public void setCode(int code) { this.code = code; }
    public String getMsg() { return msg; }
    public void setMsg(String msg) { this.msg = msg; }
    public T getData() { return data; }
    public void setData(T data) { this.data = data; }
}

package com.qusu.mybiomni.common.constant;

public enum ResponseEnum {
    SUCCESS(200, "SUCCESS"),
    ILLEGAL_PARAMETER(10201, "参数错误"),
    ILLEGAL_CODE(10202, "验证码过期或错误，请重新输入"),
    ILLEGAL_USER(10203, "账号或密码错误"),
    ILLEGAL_ADD_USER(10204, "微信账号或者名称不正确"),
    ILLEGAL_ADD_USER_EXIST(10205, "手机号码已存在，请勿重复添加"),
    ILLEGAL_NEWPASSWORD(10206, "密码必须包含6位数字或者字母"),


    USER_NOT_LOGIN(10400, "用户未登陆"),
    ILLEGAL_USER_PHONE(10401, "用户手机号码是空的"),
    ILLEGAL_FILE_TYPE(10402, "不支持的文件类型"),
    INVALID_PERMISSION(10403,"无权操作"),
    USER_NOT_EXIST(10404, "User not found"),
    USER_EMAIL_EXIST(10405, "用户邮箱已存在"),
    ILLEGAL_PASSWORD(19205, "密码修改有误，请重试"),
    NO_PRIVILEDGE(10400, "权限不足"),

    BILL_ERROR(10401, "账单查询失败"),

    INTERNAL_SERVER_ERROR(500, "系统开小差了，请稍后再试"), ;

    private final int code;
    private final String msg;

    ResponseEnum(int code, String msg) {
        this.code = code;
        this.msg = msg;
    }

    public static ResponseEnum getByCode(int code) {
        for (ResponseEnum en : ResponseEnum.values()) {
            if (en.getCode() == code) {
                return en;
            }
        }
        return null;
    }

    public String getMsg() {
        return msg;
    }

    public int getCode() {
        return code;
    }
}

package com.qusu.mybiomni.common.util;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

public class Base64Utils {

    public static String encode(String str) {
        return Base64.getUrlEncoder().encodeToString(str.getBytes(StandardCharsets.UTF_8));
    }

    public static String decode(String encodedStr) {
        return new String(Base64.getUrlDecoder().decode(encodedStr), StandardCharsets.UTF_8);
    }
}
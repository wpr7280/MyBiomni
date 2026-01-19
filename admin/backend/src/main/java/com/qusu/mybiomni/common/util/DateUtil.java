package com.qusu.mybiomni.common.util;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.Date;

public class DateUtil {

    // 定义线程安全的 DateTimeFormatter
    private static final DateTimeFormatter DATE_FORMATTER_YYYY_MM_DD = DateTimeFormatter.ofPattern("yyyy-MM-dd");

    /**
     * 检查日期字符串是否是有效的 "yyyy-MM-dd" 格式
     *
     * @param date 日期字符串
     * @return 如果是有效日期，返回 true；否则返回 false
     */
    public static boolean isValidDate(String date) {
        try {
            // 使用 LocalDate 解析日期字符串
            LocalDate.parse(date, DATE_FORMATTER_YYYY_MM_DD);
            return true; // 解析成功，说明日期格式正确
        } catch (DateTimeParseException e) {
            return false;
        }
    }

    /**
     * 将 "yyyy-MM-dd" 格式的字符串转换为 LocalDate 对象
     *
     * @param dateStr 日期字符串
     * @return 转换后的 LocalDate 对象；如果解析失败，返回 null
     */
    public static LocalDate convertYYYYMMDDToLocalDate(String dateStr) {
        try {
            return LocalDate.parse(dateStr, DATE_FORMATTER_YYYY_MM_DD);
        } catch (DateTimeParseException e) {
            return null;
        }
    }

    /**
     * 将 LocalDate 对象格式化为 "yyyy-MM-dd" 格式的字符串
     *
     * @param localDate LocalDate 对象
     * @return 格式化后的日期字符串
     */
    public static String convertLocalDateToYYYYMMDD(LocalDate localDate) {
        return localDate.format(DATE_FORMATTER_YYYY_MM_DD);
    }

    /**
     * 将 "yyyy-MM-dd" 格式的字符串转换为 Date 对象
     *
     * @param dateStr 日期字符串
     * @return 转换后的 Date 对象；如果解析失败，返回 null
     */
    public static Date convertYYYYMMDDToDate(String dateStr) {
        LocalDate localDate = convertYYYYMMDDToLocalDate(dateStr);
        if (localDate != null) {
            return Date.from(localDate.atStartOfDay(ZoneId.systemDefault()).toInstant());
        }
        return null;
    }

    /**
     * 将 Date 对象转换为 "yyyy-MM-dd" 格式的字符串
     *
     * @param date Date 对象
     * @return 格式化后的日期字符串
     */
    public static String convertDateToYYYYMMDD(Date date) {
        if (date != null) {
            LocalDate localDate = date.toInstant().atZone(ZoneId.systemDefault()).toLocalDate();
            return convertLocalDateToYYYYMMDD(localDate);
        }
        return null;
    }

    /**
     * 判断 startTime 是否在当天或之前
     *
     * @param startTime 输入的日期字符串 (格式为 yyyy-MM-dd)
     * @return 如果 startTime 在当天或之前返回 true，否则返回 false
     */
    public static boolean isCurrentOrPast(String startTime) {
        try {
            // 将输入的字符串解析为 LocalDate
            LocalDate inputDate = LocalDate.parse(startTime, DATE_FORMATTER_YYYY_MM_DD);
            // 获取当前日期
            LocalDate today = LocalDate.now();

            // 比较日期
            return !inputDate.isAfter(today); // 如果 inputDate 不在 today 之后，返回 true
        } catch (Exception e) {
            // 如果解析出错，返回 false
            System.err.println("Invalid date format: " + startTime);
            return false;
        }
    }
    public static boolean isCurrentOrPast(Date startTime) {
        try {
            if (startTime == null) {
                throw new IllegalArgumentException("startTime cannot be null");
            }
            // 将 Date 转换为 LocalDate
            LocalDate inputDate = startTime.toInstant().atZone(ZoneId.systemDefault()).toLocalDate();
            // 获取当前日期
            LocalDate today = LocalDate.now();
            // 比较日期：如果 inputDate 不在 today 之后，返回 true
            return !inputDate.isAfter(today);
        } catch (Exception e) {
            // 如果解析出错，返回 false
            System.err.println("Invalid date format: " + startTime);
            return false;
        }
    }

    /**
     * 判断 startTime 是否在 endTime 之前
     *
     * @param startTime 开始时间
     * @param endTime   结束时间
     * @return 如果 startTime 在 endTime 之前，返回 true；否则返回 false
     */
    public static boolean isStartTimeBeforeEndTime(Date startTime, Date endTime) {
        if (startTime == null || endTime == null) {
            throw new IllegalArgumentException("startTime and endTime cannot be null");
        }

        // 比较两个日期
        return startTime.before(endTime);
    }

    public static Date toDate(LocalDateTime localDateTime) {
        return Date.from(localDateTime.atZone(ZoneId.systemDefault()).toInstant());
    }
}

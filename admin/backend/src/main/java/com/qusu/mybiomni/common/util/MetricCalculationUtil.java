package com.qusu.mybiomni.common.util;


import java.math.BigDecimal;
import java.math.RoundingMode;

public class MetricCalculationUtil {

    /**
     * 保留指定小数位数
     */
    public static Double roundToDecimalPlaces(Double value, int places) {
        if (value == null) {
            return 0.0;
        }

        BigDecimal bd = BigDecimal.valueOf(value);
        bd = bd.setScale(places, RoundingMode.HALF_DOWN);
        return bd.doubleValue();
    }

    /**
     * 字节转GiB
     */
    public static Double bytesToGib(Double bytes) {
        if (bytes == null || bytes <= 0) {
            return 0.0;
        }

        return bytes / Math.pow(1024, 3);
    }

    /**
     * 计算采样时间间隔对应的小时数
     */
    public static Double samplesToHours(Long sampleCount, int intervalSeconds) {
        if (sampleCount == null || sampleCount <= 0) {
            return 0.0;
        }

        return (double) sampleCount * intervalSeconds / 3600.0;
    }
}
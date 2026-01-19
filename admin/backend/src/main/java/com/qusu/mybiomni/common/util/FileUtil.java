package com.qusu.mybiomni.common.util;

import org.apache.commons.lang3.StringUtils;
import org.apache.logging.log4j.util.Strings;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class FileUtil {
    private static final Set<String> ALLOWED_FILE_TYPES = new HashSet<>(Arrays.asList("pdf", "csv"));

    public static String getFileName(String fileName) {
        return fileName.substring(0, fileName.lastIndexOf("."));
    }

    public static String getFileType(String fileName) {
        if (StringUtils.isBlank(fileName)) {
            return Strings.EMPTY;
        }
        int lastDotIndex = fileName.lastIndexOf(".");
        if (lastDotIndex == -1 || lastDotIndex == fileName.length() - 1) {
            return Strings.EMPTY;
        }
        return fileName.substring(lastDotIndex + 1);
    }

    public static boolean isValidFile(String fileName) {
        String fileType = getFileType(fileName);
        return ALLOWED_FILE_TYPES.contains(fileType);
    }

    public static String removeFileExtension(String fileName) {
        int dotIndex = fileName.lastIndexOf(".");
        if (dotIndex > 0) {
            return fileName.substring(0, dotIndex);
        }
        return fileName; // 如果没有后缀名，直接返回文件名
    }

    public static String changeExtensionToMd(String filePath) {
        // 找到最后一个 '.' 的位置
        int dotIndex = filePath.lastIndexOf('.');

        // 修改后缀为 .md，如果没有后缀则直接追加 .md
        return (dotIndex == -1) ? filePath + ".md" : filePath.substring(0, dotIndex) + ".md";
    }

    public static boolean isFileExists(String localFilePath) {
        Path filePath = Paths.get(localFilePath);
        return Files.exists(filePath) && Files.isRegularFile(filePath);
    }
}

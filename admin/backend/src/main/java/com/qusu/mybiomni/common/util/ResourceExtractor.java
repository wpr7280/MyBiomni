package com.qusu.mybiomni.common.util;

import java.io.*;
import java.nio.file.Paths;

public class ResourceExtractor {

    /**
     * 将 JAR 中的资源文件提取到临时目录，并返回绝对路径
     *
     * @param resourcePath JAR 内部资源路径
     * @return 提取后的文件绝对路径
     * @throws IOException 如果提取文件失败
     */
    public static String extractResource(String resourcePath) throws IOException {
        // 获取资源流
        InputStream resourceStream = ResourceExtractor.class.getClassLoader().getResourceAsStream(resourcePath);
        if (resourceStream == null) {
            throw new FileNotFoundException("资源文件未找到: " + resourcePath);
        }

        // 创建临时文件
        File tempFile = File.createTempFile("resource-", "-" + Paths.get(resourcePath).getFileName());
        tempFile.deleteOnExit(); // JVM 退出时删除临时文件

        // 将资源内容写入临时文件
        try (OutputStream outputStream = new FileOutputStream(tempFile)) {
            byte[] buffer = new byte[1024];
            int bytesRead;
            while ((bytesRead = resourceStream.read(buffer)) != -1) {
                outputStream.write(buffer, 0, bytesRead);
            }
        }

        return tempFile.getAbsolutePath();
    }

//    public static void main(String[] args) {
//        try {
//            // 提取资源文件
//            String scriptPath = extractResource("python/pdf_to_md.py");
//            System.out.println("脚本提取到: " + scriptPath);
//
//            // 使用提取的脚本路径调用 Python
//            // 示例：ProcessBuilder 或其他调用方法
//        } catch (IOException e) {
//            e.printStackTrace();
//        }
//    }
}

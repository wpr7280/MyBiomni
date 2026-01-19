package com.qusu.mybiomni.common.response;

/**
 * 基础的分页查询
 */
import com.qusu.mybiomni.common.constant.ResponseEnum;

import java.util.List;

public class PageResult<T> extends BaseResult {
    private int currentPage;
    private int pageSize;
    private int totalPage;
    private long totalCount;

    public PageResult() {}

    public static <T> PageResult<T> success(T data, int currentPage,
                                            int pageSize, int totalPage, long totalCount) {
        PageResult<T> result = new PageResult<>();
        result.setCode(200);
        result.setMsg("success");
        result.setData(data);
        result.setCurrentPage(currentPage);
        result.setPageSize(pageSize);
        result.setTotalPage(totalPage);
        result.setTotalCount(totalCount);
        return result;
    }
    public static <T> PageResult<T> convertPageResult(ResponseEnum response) {
        PageResult<T> result = new PageResult<>();
        result.setCode(response.getCode());
        result.setMsg(response.getMsg());
        return result;
    }
    // getters and setters
    public int getCurrentPage() { return currentPage; }
    public void setCurrentPage(int currentPage) { this.currentPage = currentPage; }
    public int getPageSize() { return pageSize; }
    public void setPageSize(int pageSize) { this.pageSize = pageSize; }
    public int getTotalPage() { return totalPage; }
    public void setTotalPage(int totalPage) { this.totalPage = totalPage; }
    public long getTotalCount() { return totalCount; }
    public void setTotalCount(long totalCount) { this.totalCount = totalCount; }
}

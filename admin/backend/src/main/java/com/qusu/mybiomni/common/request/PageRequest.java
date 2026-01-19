package com.qusu.mybiomni.common.request;

import lombok.ToString;

@ToString
public class PageRequest {
    private static final int DEFAULT_CURRENT_PAGE = 1;
    private static final int DEFAULT_PAGE_SIZE = 10;
    private int currentPage;
    private int pageSize;

    public PageRequest() {
    }

    public int getCurrentPage() {
        if (currentPage == 0) {
            currentPage = DEFAULT_CURRENT_PAGE;
        }
        return currentPage;
    }

    public void setCurrentPage(int currentPage) {
        if (currentPage == 0) {
            currentPage = DEFAULT_CURRENT_PAGE;
        }
        this.currentPage = currentPage;
    }

    public int getPageSize() {
        if (pageSize == 0) {
            pageSize = DEFAULT_PAGE_SIZE;
        }
        return pageSize;
    }

    public void setPageSize(int pageSize) {
        if (pageSize == 0) {
            pageSize = DEFAULT_PAGE_SIZE;
        }
        this.pageSize = pageSize;
    }

    public int getStart() {
        return (getCurrentPage() - 1) * getPageSize();
    }

}

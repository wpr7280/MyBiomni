package com.qusu.mybiomni.common.response;

import lombok.Data;

import java.util.List;

@Data
public class PageResponse<T> {
    private List<T> items;
    private Long total;
    private Integer page;
    private Integer pageSize;
    
    public PageResponse(List<T> items, Long total, Integer page, Integer pageSize) {
        this.items = items;
        this.total = total;
        this.page = page;
        this.pageSize = pageSize;
    }
    
    public static <T> PageResponse<T> of(List<T> items, Long total, Integer page, Integer pageSize) {
        return new PageResponse<>(items, total, page, pageSize);
    }
}

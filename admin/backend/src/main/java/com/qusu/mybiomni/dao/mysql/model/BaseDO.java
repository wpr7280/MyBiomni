package com.qusu.mybiomni.dao.mysql.model;

import org.apache.commons.lang3.builder.ToStringBuilder;

public class BaseDO {
    @Override
    public String toString() {
        return ToStringBuilder.reflectionToString(this);
    }
}
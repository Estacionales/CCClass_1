package com.datasense.auth.repository;

import org.springframework.stereotype.Repository;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/** 인메모리 계정 저장소. 외부 DB 없이 동작한다. */
@Repository
public class AccountRepository {
    private final Map<String, String> accounts = new ConcurrentHashMap<>();

    public void save(String email) {
        accounts.put(email, email);
    }

    public boolean exists(String email) {
        return accounts.containsKey(email);
    }
}

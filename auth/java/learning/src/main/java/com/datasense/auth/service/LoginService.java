package com.datasense.auth.service;

import com.datasense.auth.repository.AccountRepository;
import org.springframework.stereotype.Service;

import java.util.Map;

/** 로그인: 기존 흐름 (회귀 검증 대상). 가입된 이메일이면 ok, 아니면 denied. */
@Service
public class LoginService {

    private final AccountRepository accounts;

    public LoginService(AccountRepository accounts) {
        this.accounts = accounts;
    }

    public Map<String, String> login(String email) {
        String status = accounts.exists(email) ? "ok" : "denied";
        return Map.of("status", status);
    }
}

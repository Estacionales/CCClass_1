package com.datasense.auth;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.ResponseEntity;

import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * proof 4/4 · 회귀: OTP 가입 흐름을 얹어도 기존 로그인 기능이 깨지지 않는다.
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class RegressionTest {

    @Autowired
    private TestRestTemplate rest;

    @Test
    @SuppressWarnings("unchecked")
    void regressionLoginExistingAccount() {
        String email = "regression@datasense.test";

        // 가입까지 마친 기존 계정을 만든다
        String code = (String) rest.postForEntity(
                "/auth/otp/issue", Map.of("email", email), Map.class).getBody().get("code");
        rest.postForEntity("/auth/signup", Map.of("email", email, "code", code), Map.class);

        // 기존 로그인 흐름이 그대로 ok 여야 한다 (회귀 없음)
        ResponseEntity<Map> login = rest.postForEntity(
                "/auth/login", Map.of("email", email), Map.class);
        assertThat(login.getStatusCode().is2xxSuccessful()).isTrue();
        assertThat(login.getBody().get("status")).isEqualTo("ok");
    }
}

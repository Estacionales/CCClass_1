package com.datasense.auth;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.ResponseEntity;

import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * proof 3/4 · 응답 계약 정합 (화면 parity 대체).
 * REST 응답 JSON이 화면·클라이언트가 기대하는 필수 필드 계약을 지키는지 실제 HTTP로 검증한다.
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class ContractParityTest {

    @Autowired
    private TestRestTemplate rest;

    @Test
    @SuppressWarnings("unchecked")
    void otpIssueResponseContract() {                           // 발급 응답 계약: email·purpose·code
        ResponseEntity<Map> res = rest.postForEntity(
                "/auth/otp/issue", Map.of("email", "parity@datasense.test"), Map.class);
        assertThat(res.getStatusCode().is2xxSuccessful()).isTrue();
        assertThat(res.getBody()).containsKeys("email", "purpose", "code");
        assertThat((String) res.getBody().get("code")).matches("\\d{6}");
    }

    @Test
    @SuppressWarnings("unchecked")
    void signupResponseContractParity() {                       // 가입 응답 계약: status·email·idempotencyKey·replay
        String email = "parity-signup@datasense.test";
        String code = (String) rest.postForEntity(
                "/auth/otp/issue", Map.of("email", email), Map.class).getBody().get("code");
        ResponseEntity<Map> res = rest.postForEntity(
                "/auth/signup", Map.of("email", email, "code", code), Map.class);
        assertThat(res.getStatusCode().is2xxSuccessful()).isTrue();
        assertThat(res.getBody()).containsKeys("status", "email", "idempotencyKey", "replay");
        assertThat(res.getBody().get("status")).isEqualTo("created");
    }
}

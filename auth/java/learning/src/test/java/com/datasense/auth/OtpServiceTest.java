package com.datasense.auth;

import com.datasense.auth.service.OtpService;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * proof 1/4 · OTP 발급·검증·만료·잠금 (AC-1·AC-3·AC-4).
 * 가변 시계를 주입해 만료를 결정적으로 검증한다.
 */
class OtpServiceTest {

    private final long[] now = {0L};

    private OtpService newService() {
        return new OtpService(300, 5, () -> now[0]);
    }

    @Test
    void otpIssueAndVerify() {                                   // AC-1: 발급 → 검증 통과
        OtpService svc = newService();
        String code = svc.issue("a@datasense.test", "signup");
        assertThat(code).matches("\\d{6}");
        assertThat(svc.verify("a@datasense.test", code, "signup").isVerified()).isTrue();
    }

    @Test
    void otpNoIssue() {                                          // 발급 없이 검증 → no_otp
        OtpService svc = newService();
        assertThat(svc.verify("x@datasense.test", "123456", "signup").reason())
                .isEqualTo("no_otp");
    }

    @Test
    void otpWrongThenLock() {                                    // 5회 오입력 → 잠금
        OtpService svc = newService();
        String code = svc.issue("a@datasense.test", "signup");
        String wrong = "000000".equals(code) ? "111111" : "000000";
        for (int i = 0; i < 5; i++) {
            assertThat(svc.verify("a@datasense.test", wrong, "signup").status())
                    .isEqualTo("rejected");
        }
        assertThat(svc.verify("a@datasense.test", code, "signup").reason())
                .isEqualTo("locked");
    }

    @Test
    void otpExpiry() {                                           // AC-4: TTL 초과 → expired
        OtpService svc = newService();
        String code = svc.issue("a@datasense.test", "signup");
        now[0] += 301_000;                                       // 301초 경과 (TTL 300s 초과)
        assertThat(svc.verify("a@datasense.test", code, "signup").reason())
                .isEqualTo("expired");
    }
}

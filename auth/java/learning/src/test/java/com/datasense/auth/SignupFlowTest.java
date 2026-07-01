package com.datasense.auth;

import com.datasense.auth.domain.SignupResult;
import com.datasense.auth.repository.AccountRepository;
import com.datasense.auth.service.IdempotencyStore;
import com.datasense.auth.service.OtpService;
import com.datasense.auth.service.SignupService;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * proof 2/4 · 회원가입: OTP 통과 시 계정 생성, 잘못된 OTP 거부, 멱등 (AC-2·AC-3·AC-5).
 */
class SignupFlowTest {

    private AccountRepository accounts;
    private OtpService otp;
    private SignupService signup;

    private void fresh() {
        accounts = new AccountRepository();
        otp = new OtpService(300, 5, () -> 0L);
        signup = new SignupService(otp, new IdempotencyStore(), accounts);
    }

    @Test
    void signupAfterOtp() {                                      // AC-2: OTP 후 가입 → created
        fresh();
        String code = otp.issue("a@datasense.test", "signup");
        SignupResult r = signup.signup("a@datasense.test", code, "signup", null);
        assertThat(r.status()).isEqualTo("created");
        assertThat(accounts.exists("a@datasense.test")).isTrue();
    }

    @Test
    void signupRejectedWrongOtp() {                             // AC-3: 잘못된 OTP → rejected
        fresh();
        String code = otp.issue("a@datasense.test", "signup");
        String wrong = "000000".equals(code) ? "111111" : "000000";
        SignupResult r = signup.signup("a@datasense.test", wrong, "signup", null);
        assertThat(r.status()).isEqualTo("rejected");
        assertThat(r.reason()).isEqualTo("wrong_code");
    }

    @Test
    void signupIdempotent() {                                    // AC-5: 재요청 멱등 (중복 가입 없음)
        fresh();
        String code = otp.issue("a@datasense.test", "signup");
        SignupResult r1 = signup.signup("a@datasense.test", code, "signup", null);
        SignupResult r2 = signup.signup("a@datasense.test", code, "signup", null);
        assertThat(r1.idempotencyKey()).isEqualTo(r2.idempotencyKey());
        assertThat(r2.replay()).isTrue();
    }
}

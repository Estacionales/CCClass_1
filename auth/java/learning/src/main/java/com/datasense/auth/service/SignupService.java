package com.datasense.auth.service;

import com.datasense.auth.domain.OtpResult;
import com.datasense.auth.domain.SignupResult;
import com.datasense.auth.repository.AccountRepository;
import org.springframework.stereotype.Service;

/** 회원가입: OTP 검증 통과 시 계정 생성, 멱등 보장 (AC-2·AC-5). */
@Service
public class SignupService {

    private final OtpService otp;
    private final IdempotencyStore idem;
    private final AccountRepository accounts;

    public SignupService(OtpService otp, IdempotencyStore idem, AccountRepository accounts) {
        this.otp = otp;
        this.idem = idem;
        this.accounts = accounts;
    }

    public SignupResult signup(String email, String code, String purpose, String idemKey) {
        OtpResult v = otp.verify(email, code, purpose);
        if (!v.isVerified()) {
            return SignupResult.rejected(v.reason(), email);
        }

        String key = (idemKey == null || idemKey.isBlank())
                ? IdempotencyStore.idempotencyKey(email)
                : idemKey;

        IdempotencyStore.Issued issued = idem.issueOnce(key, () -> {
            accounts.save(email);
            return SignupResult.created(email, key, false);
        });
        return SignupResult.created(issued.result().email(), key, issued.replay());
    }
}

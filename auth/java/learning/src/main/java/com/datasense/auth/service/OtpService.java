package com.datasense.auth.service;

import com.datasense.auth.domain.OtpRecord;
import com.datasense.auth.domain.OtpResult;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.security.SecureRandom;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.LongSupplier;

/**
 * 회원가입 OTP: 발급·검증·만료·잠금 (TTL + 시도 제한).
 * AC-1·AC-3·AC-4.
 */
@Service
public class OtpService {

    private final long ttlSeconds;
    private final int maxAttempts;
    private final LongSupplier clock;
    private final SecureRandom random = new SecureRandom();
    private final Map<String, OtpRecord> store = new ConcurrentHashMap<>();

    @Autowired
    public OtpService(
            @Value("${auth.otp.ttl-seconds:300}") long ttlSeconds,
            @Value("${auth.otp.max-attempts:5}") int maxAttempts) {
        this(ttlSeconds, maxAttempts, System::currentTimeMillis);
    }

    /** 테스트에서 가변 시계를 주입해 만료를 결정적으로 검증한다. */
    public OtpService(long ttlSeconds, int maxAttempts, LongSupplier clock) {
        this.ttlSeconds = ttlSeconds;
        this.maxAttempts = maxAttempts;
        this.clock = clock;
    }

    /** (email, purpose)에 6자리 OTP를 발급하고 TTL을 건다. */
    public String issue(String email, String purpose) {
        String code = String.format("%06d", random.nextInt(1_000_000));
        store.put(key(email, purpose), new OtpRecord(code, now()));
        return code;
    }

    /** OTP를 검증한다. 틀리면 시도를 누적하고, maxAttempts 도달 시 잠근다. */
    public OtpResult verify(String email, String code, String purpose) {
        OtpRecord rec = store.get(key(email, purpose));
        if (rec == null) {
            return OtpResult.rejected("no_otp");
        }
        if (rec.isLocked()) {
            return OtpResult.rejected("locked");
        }
        if ((now() - rec.getIssuedAtMillis()) > ttlSeconds * 1000L) {
            return OtpResult.rejected("expired");
        }
        if (!rec.getCode().equals(code)) {
            if (rec.incrementAttempts() >= maxAttempts) {
                rec.lock();
            }
            return OtpResult.rejected("wrong_code");
        }
        return OtpResult.verified();
    }

    private long now() {
        return clock.getAsLong();
    }

    private String key(String email, String purpose) {
        return email + " " + purpose;
    }
}

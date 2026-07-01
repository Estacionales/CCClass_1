package com.datasense.auth.domain;

/** (email, purpose)에 묶인 OTP 발급 기록. TTL·시도 횟수·잠금 상태를 가진다. */
public class OtpRecord {
    private final String code;
    private final long issuedAtMillis;
    private int attempts;
    private boolean locked;

    public OtpRecord(String code, long issuedAtMillis) {
        this.code = code;
        this.issuedAtMillis = issuedAtMillis;
        this.attempts = 0;
        this.locked = false;
    }

    public String getCode() {
        return code;
    }

    public long getIssuedAtMillis() {
        return issuedAtMillis;
    }

    public int getAttempts() {
        return attempts;
    }

    public int incrementAttempts() {
        return ++attempts;
    }

    public boolean isLocked() {
        return locked;
    }

    public void lock() {
        this.locked = true;
    }
}

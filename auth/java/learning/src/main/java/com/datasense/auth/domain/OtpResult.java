package com.datasense.auth.domain;

/** OTP 검증 결과. status: verified | rejected, reason: ok | no_otp | locked | expired | wrong_code */
public record OtpResult(String status, String reason) {
    public static OtpResult verified() {
        return new OtpResult("verified", "ok");
    }

    public static OtpResult rejected(String reason) {
        return new OtpResult("rejected", reason);
    }

    public boolean isVerified() {
        return "verified".equals(status);
    }
}

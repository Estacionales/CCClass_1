package com.datasense.auth.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;

/** 회원가입 요청: 이메일 + 6자리 OTP. idemKey가 있으면 멱등 키로 사용한다. */
public record SignupRequest(
        @NotBlank @Email String email,
        @NotBlank @Pattern(regexp = "\\d{6}", message = "OTP는 6자리 숫자여야 합니다") String code,
        String purpose,
        String idemKey) {

    public String purposeOrDefault() {
        return (purpose == null || purpose.isBlank()) ? "signup" : purpose;
    }
}

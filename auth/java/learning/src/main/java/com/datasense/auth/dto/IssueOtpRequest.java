package com.datasense.auth.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

/** OTP 발급 요청. purpose 미지정 시 signup으로 처리한다. */
public record IssueOtpRequest(
        @NotBlank @Email String email,
        String purpose) {

    public String purposeOrDefault() {
        return (purpose == null || purpose.isBlank()) ? "signup" : purpose;
    }
}

package com.datasense.auth.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

/** 로그인 요청: 가입된 이메일이면 ok, 아니면 denied. */
public record LoginRequest(
        @NotBlank @Email String email) {
}

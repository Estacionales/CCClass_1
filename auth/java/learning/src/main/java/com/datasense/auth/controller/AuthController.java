package com.datasense.auth.controller;

import com.datasense.auth.domain.SignupResult;
import com.datasense.auth.dto.IssueOtpRequest;
import com.datasense.auth.dto.LoginRequest;
import com.datasense.auth.dto.SignupRequest;
import com.datasense.auth.service.LoginService;
import com.datasense.auth.service.OtpService;
import com.datasense.auth.service.SignupService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/** OTP 인증 엔드포인트: 발급 → 검증·가입 → 로그인. */
@RestController
@RequestMapping("/auth")
public class AuthController {

    private final OtpService otpService;
    private final SignupService signupService;
    private final LoginService loginService;

    public AuthController(OtpService otpService, SignupService signupService, LoginService loginService) {
        this.otpService = otpService;
        this.signupService = signupService;
        this.loginService = loginService;
    }

    /** OTP 발급 (AC-1). 데모 편의상 발급된 code를 응답에 포함한다. */
    @PostMapping("/otp/issue")
    public ResponseEntity<Map<String, String>> issueOtp(@Valid @RequestBody IssueOtpRequest req) {
        String code = otpService.issue(req.email(), req.purposeOrDefault());
        return ResponseEntity.ok(Map.of(
                "email", req.email(),
                "purpose", req.purposeOrDefault(),
                "code", code));
    }

    /** OTP 검증 후 회원가입 (AC-2·AC-3·AC-4·AC-5). */
    @PostMapping("/signup")
    public ResponseEntity<SignupResult> signup(@Valid @RequestBody SignupRequest req) {
        SignupResult result = signupService.signup(
                req.email(), req.code(), req.purposeOrDefault(), req.idemKey());
        HttpStatus status = "created".equals(result.status())
                ? HttpStatus.CREATED
                : HttpStatus.UNPROCESSABLE_ENTITY;
        return ResponseEntity.status(status).body(result);
    }

    /** 로그인 (회귀 대상). */
    @PostMapping("/login")
    public ResponseEntity<Map<String, String>> login(@Valid @RequestBody LoginRequest req) {
        return ResponseEntity.ok(loginService.login(req.email()));
    }
}

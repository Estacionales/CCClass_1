package com.datasense.auth.domain;

/** 회원가입 결과. status: created | rejected, replay: 멱등 재요청 여부. */
public record SignupResult(String status, String reason, String email,
                           String idempotencyKey, boolean replay) {

    public static SignupResult created(String email, String idempotencyKey, boolean replay) {
        return new SignupResult("created", "ok", email, idempotencyKey, replay);
    }

    public static SignupResult rejected(String reason, String email) {
        return new SignupResult("rejected", reason, email, "", false);
    }
}

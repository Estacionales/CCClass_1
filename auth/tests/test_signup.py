# -*- coding: utf-8 -*-
"""회원가입 — OTP 통과 시 계정 생성, 멱등."""


def test_signup_after_otp(signup):
    sv, otp, _ = signup
    otp.issue("a@x.com")
    r = sv.signup("a@x.com", "123456")
    assert r.status == "created"
    assert "a@x.com" in sv.accounts


def test_signup_rejected_wrong_otp(signup):
    sv, otp, _ = signup
    otp.issue("a@x.com")
    r = sv.signup("a@x.com", "000000")
    assert r.status == "rejected" and r.reason == "wrong_code"


def test_signup_idempotent(signup):
    sv, otp, _ = signup
    otp.issue("a@x.com")
    r1 = sv.signup("a@x.com", "123456")
    r2 = sv.signup("a@x.com", "123456")  # 재요청
    assert r1.idempotency_key == r2.idempotency_key
    assert r2.replay is True
    assert len(sv.accounts) == 1  # 중복 계정 없음

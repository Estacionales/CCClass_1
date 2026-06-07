# -*- coding: utf-8 -*-
"""OTP 발급·검증·만료·잠금."""


def test_otp_issue_and_verify(otp):
    svc, _ = otp
    assert svc.issue("a@x.com") == "123456"
    assert svc.verify("a@x.com", "123456").status == "verified"


def test_otp_no_issue(otp):
    svc, _ = otp
    assert svc.verify("x@x.com", "123456").reason == "no_otp"


def test_otp_wrong_then_lock(otp):
    svc, _ = otp
    svc.issue("a@x.com")
    for _ in range(5):
        assert svc.verify("a@x.com", "000000").status == "rejected"
    assert svc.verify("a@x.com", "123456").reason == "locked"  # 5회 실패 → 잠금


def test_otp_expiry(otp):
    svc, clock = otp
    svc.issue("a@x.com")
    clock["t"] += 301  # TTL(300s) 초과
    assert svc.verify("a@x.com", "123456").reason == "expired"

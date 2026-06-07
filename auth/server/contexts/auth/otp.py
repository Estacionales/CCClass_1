# -*- coding: utf-8 -*-
"""회원가입 OTP — 발급·검증·만료·잠금 (TTL + 시도 제한).

clock·otp_gen 을 주입해 결정적으로 테스트한다(실시간·난수 비의존).
"""
import random
import time
from dataclasses import dataclass


@dataclass
class OTPResult:
    status: str  # verified | rejected
    reason: str = ""


class OTPService:
    def __init__(self, *, ttl_s=300, max_attempts=5, clock=None, otp_gen=None):
        self.ttl_s = ttl_s
        self.max_attempts = max_attempts
        self._clock = clock or time.time
        self._gen = otp_gen or (lambda: f"{random.randint(0, 999999):06d}")
        self._store = {}

    def issue(self, email, purpose="signup"):
        code = self._gen()
        self._store[(email, purpose)] = {
            "code": code, "issued": self._clock(), "attempts": 0, "locked": False}
        return code

    def verify(self, email, code, purpose="signup"):
        rec = self._store.get((email, purpose))
        if rec is None:
            return OTPResult("rejected", "no_otp")
        if rec["locked"]:
            return OTPResult("rejected", "locked")
        if self._clock() - rec["issued"] > self.ttl_s:
            return OTPResult("rejected", "expired")
        if code != rec["code"]:
            rec["attempts"] += 1
            if rec["attempts"] >= self.max_attempts:
                rec["locked"] = True
            return OTPResult("rejected", "wrong_code")
        return OTPResult("verified", "ok")

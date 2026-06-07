# -*- coding: utf-8 -*-
"""같은 기능('회원가입 OTP')의 두 구현 — 명세 없이(vibe) vs 명세 기반(SDD).

차이는 코드 실력이 아니라 **무엇을 '맞는 동작'으로 정의했는가**다. 시간은 t(정수)로 주입해
결정적으로 채점한다(실시간·난수 비의존).
"""


class VibeOtp:
    """명세 없이 'happy path'만 구현. 만료·잠금·멱등은 아무도 명세하지 않아 빠졌다."""
    TTL = 300

    def __init__(self):
        self.codes = {}
        self.created = []          # 멱등 없음: 부를 때마다 append

    def issue(self, email, t=0):
        self.codes[email] = ("123456", t)
        return "123456"

    def verify(self, email, code, t=0):
        rec = self.codes.get(email)
        return bool(rec) and rec[0] == code   # 만료·시도제한 검사 없음

    def signup(self, email, code, t=0):
        if not self.verify(email, code, t):
            return False
        self.created.append(email)            # 중복 가입 차단 없음
        return True


class SddOtp:
    """EARS 수용기준대로: 만료(AC-2)·잠금(AC-3)·멱등(AC-4)을 '맞는 동작'으로 박았다."""
    TTL = 300
    MAX_ATTEMPTS = 5

    def __init__(self):
        self.codes = {}
        self.created = set()       # 멱등: 같은 사용자는 한 번만

    def issue(self, email, t=0):
        self.codes[email] = {"code": "123456", "t": t, "fails": 0, "locked": False}
        return "123456"

    def verify(self, email, code, t=0):
        r = self.codes.get(email)
        if not r or r["locked"]:
            return False
        if t - r["t"] > self.TTL:             # AC-2 만료
            return False
        if code != r["code"]:
            r["fails"] += 1
            if r["fails"] >= self.MAX_ATTEMPTS:   # AC-3 잠금
                r["locked"] = True
            return False
        return True

    def signup(self, email, code, t=0):
        if not self.verify(email, code, t):
            return False
        self.created.add(email)               # AC-4 멱등
        return True

# -*- coding: utf-8 -*-
"""EARS 수용기준을 코드로 — 두 구현을 같은 기준으로 채점한다.

명세(spec)가 곧 '무엇이 맞는가'의 정의다. 같은 4개 기준을 vibe·SDD 양쪽에 똑같이 돌린다.
"""

CRITERIA = [
    ("AC-1 정상 발급·검증", "유효한 OTP로 가입 성공"),
    ("AC-2 만료 OTP 거부", "TTL(300s) 지난 OTP는 거부"),
    ("AC-3 5회 오류 잠금", "5회 틀리면 정답도 거부(무차별 차단)"),
    ("AC-4 재요청 멱등", "같은 가입 두 번이어도 계정 1개"),
]


def run(make):
    """make: () -> OTP 구현 인스턴스. 각 기준을 독립 인스턴스로 채점."""
    r = {}

    o = make(); o.issue("a@x.com", t=0)
    r["AC-1 정상 발급·검증"] = (o.signup("a@x.com", "123456", t=10) is True)

    o = make(); o.issue("a@x.com", t=0)
    r["AC-2 만료 OTP 거부"] = (o.signup("a@x.com", "123456", t=999) is False)

    o = make(); o.issue("a@x.com", t=0)
    for _ in range(5):
        o.signup("a@x.com", "000000", t=10)          # 5회 오답
    r["AC-3 5회 오류 잠금"] = (o.signup("a@x.com", "123456", t=10) is False)  # 잠겨서 정답도 거부

    o = make(); o.issue("a@x.com", t=0)
    o.signup("a@x.com", "123456", t=10)
    o.signup("a@x.com", "123456", t=10)              # 재요청
    r["AC-4 재요청 멱등"] = (len(o.created) == 1)

    return r

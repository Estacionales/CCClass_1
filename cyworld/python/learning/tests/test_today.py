# -*- coding: utf-8 -*-
"""투데이: 하루 한 번만 등록, 같은 날짜 재요청은 멱등."""


def test_check_in_first_time(today):
    r = today.check_in("u1", "2026-07-02")
    assert r.status == "recorded"


def test_check_in_idempotent_same_day(today):
    today.check_in("u1", "2026-07-02")
    r2 = today.check_in("u1", "2026-07-02")  # 같은 날 재요청
    assert r2.status == "already" and r2.reason == "already_checked_in"


def test_check_in_new_day_allowed(today):
    today.check_in("u1", "2026-07-02")
    r2 = today.check_in("u1", "2026-07-03")  # 날짜 변경
    assert r2.status == "recorded"

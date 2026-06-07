# -*- coding: utf-8 -*-
"""AC-5 — 동의 철회 시 처리 중단·파기하고 동의 원장에 기록한다."""


def test_ac5_withdraw_stops_processing(orch, agency_ok_fn):
    o, consent, elig, _ = orch
    consent.grant("u1")
    elig.satisfy("u1", "세대주 동의")
    assert o.issue("u1", "전입신고", responder=agency_ok_fn).status == "issued"

    o.handle_withdrawal("u1")  # 철회 → 중단·파기·원장 기록

    assert consent.is_active("u1") is False
    assert o.issued_count("u1") == 0  # 수집·발급 데이터 파기
    after = o.issue("u1", "전입신고", responder=agency_ok_fn)
    assert after.status == "rejected"
    assert after.reason == "consent_required"


def test_ac5_ledger_is_append_only(orch, agency_ok_fn):
    o, consent, elig, _ = orch
    consent.grant("u1")
    elig.satisfy("u1", "세대주 동의")
    o.issue("u1", "전입신고", responder=agency_ok_fn)
    o.handle_withdrawal("u1")
    statuses = [r.status for r in consent.records() if r.user_id == "u1"]
    assert statuses == ["granted", "withdrawn"]  # 덮어쓰지 않고 누적

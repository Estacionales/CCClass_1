# -*- coding: utf-8 -*-
"""AC-4 — 발급·정산 배치가 재실행돼도 중복을 만들지 않는다 (멱등)."""
from server.contexts.eminwon.issue_svc import IssueResult
from server.contexts.settlement.batch import SettlementLedger, run_settlement


def test_ac4_issue_is_idempotent(orch, agency_ok_fn):
    o, consent, elig, _ = orch
    consent.grant("u1")
    elig.satisfy("u1", "세대주 동의")
    r1 = o.issue("u1", "전입신고", responder=agency_ok_fn)
    r2 = o.issue("u1", "전입신고", responder=agency_ok_fn)  # 재요청
    assert r1.idempotency_key == r2.idempotency_key
    assert r1.replay is False
    assert r2.replay is True            # 두 번째는 재생 — 중복 발급 아님
    assert o.issued_count("u1") == 1    # 발급은 1건만


def test_ac4_settlement_no_duplicate():
    issuances = [
        IssueResult(status="issued", idempotency_key="k1"),
        IssueResult(status="issued", idempotency_key="k2"),
    ]
    ledger = SettlementLedger()
    fees1 = run_settlement(issuances, ledger)
    fees2 = run_settlement(issuances, ledger)  # 배치 재실행
    assert len(fees1) == 2
    assert len(fees2) == 0  # 중복 정산 0건

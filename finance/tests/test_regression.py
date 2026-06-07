# -*- coding: utf-8 -*-
"""회귀 — 새 기능(발급) 외 공유 표면(자격검증·정산·원장)이 무손상인지 (shared surface)."""
from server.contexts.eminwon.issue_svc import IssueResult
from server.contexts.settlement.batch import SettlementLedger, run_settlement
from server.shared import rules


def test_regression_other_minwon_eligibility():
    # 발급 기능과 무관한 다른 민원 자격검증 흐름이 그대로 동작
    assert rules.required_documents("사업자등록") == ["사업자등록증", "임대차계약서"]
    assert rules.required_documents("복지급여신청") == ["주민등록표", "소득증명원"]


def test_regression_unknown_minwon_is_blocked():
    import pytest
    with pytest.raises(rules.UnknownMinwon):
        rules.required_documents("없는민원")


def test_regression_settlement_totals():
    issuances = [IssueResult(status="issued", idempotency_key=f"k{i}") for i in range(5)]
    ledger = SettlementLedger()
    fees = run_settlement(issuances, ledger)
    assert sum(f["fee"] for f in fees) == 5 * 1000  # 정산 합계 무손상

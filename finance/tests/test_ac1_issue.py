# -*- coding: utf-8 -*-
"""AC-1 — 동의 완료 후 발급 요청 시 자격 규칙으로 서류를 산출·수집한다."""


def test_ac1_issue_after_consent(orch, agency_ok_fn):
    o, consent, elig, _ = orch
    consent.grant("u1")
    elig.satisfy("u1", "세대주 동의")
    res = o.issue("u1", "전입신고", responder=agency_ok_fn)
    assert res.status == "issued"
    assert "주민등록표" in res.documents
    assert res.idempotency_key
    assert res.degraded is False


def test_ac1_reject_without_consent(orch, agency_ok_fn):
    o, _, elig, _ = orch
    elig.satisfy("u1", "세대주 동의")  # 자격은 있어도 동의가 없으면 거부
    res = o.issue("u1", "전입신고", responder=agency_ok_fn)
    assert res.status == "rejected"
    assert res.reason == "consent_required"

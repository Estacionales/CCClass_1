# -*- coding: utf-8 -*-
"""AC-3: 근거 규정 여러 단계 조회: '있다'가 아니라 '맞다'(경로 일치)까지 검증."""
from server.contexts.advisory import citation
from server.shared import rules


def test_ac3_citation_path_is_exact():
    steps, citations = rules.trace("전입신고")
    # 민원 → 필요서류 → 근거규정 → 예외 를 끝까지
    assert citations == ["주민등록표", "전자정부법 §9", "세대주 동의"]
    assert [s.relation for s in steps] == ["필요서류", "근거규정", "예외"]


def test_ac3_advisory_exactness():
    ans = citation.answer("전입신고", eligible=True)
    assert ans["status"] == "answered"
    assert ans["exactness"] == "3/3"


def test_ac3_guardrail_refuses_when_ineligible(orch, agency_ok_fn):
    o, consent, elig, _ = orch
    consent.grant("u2")  # 동의는 있으나 예외(세대주 동의) 미충족
    res = o.issue("u2", "전입신고", responder=agency_ok_fn)
    assert res.status == "rejected"
    assert res.reason == "exception_unmet"
    assert "전자정부법 §9" in res.citations  # 거부해도 근거는 인용

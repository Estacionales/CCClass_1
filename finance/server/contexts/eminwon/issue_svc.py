# -*- coding: utf-8 -*-
"""전자민원 발급 오케스트레이션.

흐름: 동의 확인(AC-1) → 자격·예외 가드레일(AC-3) → 서류 산출 → 기관 수집(AC-2)
      → 멱등 발급(AC-4). 동의 철회 시 처리 중단·파기(AC-5).
"""
from dataclasses import dataclass, field, replace

from server.contexts.eminwon.idem import IdempotencyStore, idempotency_key
from server.shared import eligibility as eligibility_mod
from server.shared import rules


@dataclass
class IssueResult:
    status: str  # issued | rejected
    reason: str = ""
    documents: list = field(default_factory=list)
    citations: list = field(default_factory=list)
    idempotency_key: str = ""
    replay: bool = False
    degraded: bool = False


class IssueOrchestrator:
    def __init__(self, consent, adapter, eligibility, idem=None):
        self.consent = consent
        self.adapter = adapter
        self.eligibility = eligibility
        self.idem = idem or IdempotencyStore()
        self._issued = {}  # user_id -> [idempotency_key] (파기 대상 추적)

    def issue(self, user_id, minwon_type, *, responder, idem_key=None):
        # AC-1: 동의 게이트 — 동의가 없거나 철회되면 처리 중단
        if not self.consent.is_active(user_id):
            return IssueResult(status="rejected", reason="consent_required")

        # 미등록 민원 유형 차단
        try:
            _, citations = rules.trace(minwon_type)
        except rules.UnknownMinwon:
            return IssueResult(status="rejected", reason="unknown_minwon")

        # AC-3: 가드레일 — 예외 조건(자격) 미충족 시 거부 (근거는 인용해 둠)
        if not self.eligibility.is_eligible(user_id, minwon_type):
            return IssueResult(status="rejected", reason="exception_unmet",
                               citations=citations)

        docs = eligibility_mod.required_documents(minwon_type)
        key = idem_key or idempotency_key({"user": user_id, "minwon": minwon_type})

        def _do():
            degraded = False
            for d in docs:
                r = self.adapter.collect(d, responder=responder)
                degraded = degraded or r.degraded
            return IssueResult(status="issued", documents=docs, citations=citations,
                               idempotency_key=key, degraded=degraded)

        result, replayed = self.idem.issue_once(key, _do)
        if not replayed:
            self._issued.setdefault(user_id, []).append(key)
        return replace(result, replay=replayed)

    # --- AC-5: 동의 철회 → 중단·파기·원장 기록 ---
    def issued_count(self, user_id):
        return len(self._issued.get(user_id, []))

    def handle_withdrawal(self, user_id, scope="mydata"):
        self.consent.withdraw(user_id, scope)   # 원장에 철회 기록(append)
        self._issued.pop(user_id, None)          # 수집·발급 데이터 파기

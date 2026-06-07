# -*- coding: utf-8 -*-
"""연계 게이트웨이 어댑터 — 재시도 → 서킷브레이커 → 대체 경로 (AC-2 회복력).

기관 응답을 responder(doc_code, attempt) 콜러블로 주입한다.
TimeoutError를 던지면 '3초 내 미응답'을 시뮬레이션한다.
"""
from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class CollectResult:
    doc_code: str
    data: Any
    source: str  # agency | fallback
    attempts: int
    fallback: bool = False
    degraded: bool = False


class GatewayAdapter:
    def __init__(self, *, max_retries=3, failure_threshold=3,
                 fallback_route: Optional[Callable[[str], Any]] = None):
        self.max_retries = max_retries
        self.failure_threshold = failure_threshold
        self.fallback_route = fallback_route
        self.attempts = 0
        self.fallback_used = False
        self._consecutive_failures = 0
        self._circuit_open = False

    @property
    def circuit_open(self):
        return self._circuit_open

    def collect(self, doc_code, *, responder):
        if self._circuit_open:
            return self._fallback(doc_code)
        for attempt in range(1, self.max_retries + 1):
            self.attempts += 1
            try:
                data = responder(doc_code, attempt)
            except TimeoutError:
                self._consecutive_failures += 1
                if self._consecutive_failures >= self.failure_threshold:
                    self._circuit_open = True
                    break
                continue
            self._consecutive_failures = 0
            return CollectResult(doc_code, data, source="agency",
                                 attempts=attempt, fallback=False)
        return self._fallback(doc_code)

    def _fallback(self, doc_code):
        self.fallback_used = True
        data = self.fallback_route(doc_code) if self.fallback_route else None
        return CollectResult(doc_code, data, source="fallback",
                             attempts=self.attempts, fallback=True, degraded=True)

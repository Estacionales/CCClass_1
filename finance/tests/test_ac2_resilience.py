# -*- coding: utf-8 -*-
"""AC-2 — 기관 미응답 시 재시도3 → 서킷브레이커 → 대체 경로(graceful degradation)."""
from server.integration.adapters.gw.base_adapter import GatewayAdapter


def test_ac2_retry_circuit_fallback(agency_timeout_fn):
    adapter = GatewayAdapter(max_retries=3, failure_threshold=3,
                             fallback_route=lambda d: {"doc": d, "via": "fallback"})
    res = adapter.collect("주민등록표", responder=agency_timeout_fn)
    assert adapter.attempts == 3        # 재시도 3회
    assert adapter.circuit_open is True  # 서킷 오픈
    assert res.fallback is True          # 대체 경로
    assert res.degraded is True          # 우아하게 저하 (예외 미전파)
    assert res.data == {"doc": "주민등록표", "via": "fallback"}


def test_ac2_recovers_on_late_success():
    def flaky(doc, attempt):
        if attempt < 2:
            raise TimeoutError()
        return {"doc": doc}

    adapter = GatewayAdapter()
    res = adapter.collect("주민등록표", responder=flaky)
    assert res.fallback is False
    assert res.source == "agency"
    assert res.attempts == 2

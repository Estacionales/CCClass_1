# -*- coding: utf-8 -*-
"""발급 수수료 정산 배치 — 재실행해도 중복 정산을 만들지 않는다 (AC-4 멱등)."""

FEE_PER_ISSUE = 1000


class SettlementLedger:
    """이미 정산한 idempotency_key 집합."""

    def __init__(self):
        self.settled_keys = set()


def run_settlement(issuances, ledger):
    """발급 건당 수수료를 정산한다. 같은 키는 한 번만 정산(멱등)."""
    fees = []
    for iss in issuances:
        key = iss.idempotency_key
        if not key or key in ledger.settled_keys:
            continue  # 이미 정산됨 → 중복 방지
        ledger.settled_keys.add(key)
        fees.append({"key": key, "fee": FEE_PER_ISSUE})
    return fees

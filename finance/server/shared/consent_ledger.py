# -*- coding: utf-8 -*-
"""동의 원장 — 부여·철회·만료를 append-only로 기록 (AC-5)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ConsentRecord:
    user_id: str
    scope: str
    status: str  # granted | withdrawn | expired
    seq: int


class ConsentLedger:
    """append-only 동의 원장. 최신 레코드가 현재 상태를 결정한다."""

    def __init__(self):
        self._records = []

    def _append(self, user_id, scope, status):
        rec = ConsentRecord(user_id, scope, status, len(self._records) + 1)
        self._records.append(rec)
        return rec

    def grant(self, user_id, scope="mydata"):
        return self._append(user_id, scope, "granted")

    def withdraw(self, user_id, scope="mydata"):
        return self._append(user_id, scope, "withdrawn")

    def expire(self, user_id, scope="mydata"):
        return self._append(user_id, scope, "expired")

    def is_active(self, user_id, scope="mydata"):
        latest = None
        for r in self._records:
            if r.user_id == user_id and r.scope == scope:
                latest = r
        return latest is not None and latest.status == "granted"

    def records(self):
        return list(self._records)

    def count(self):
        return len(self._records)

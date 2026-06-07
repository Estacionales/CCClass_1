# -*- coding: utf-8 -*-
"""멱등 처리 — idempotency_key로 중복 발급/정산을 차단한다 (AC-4)."""
import hashlib
import json


def idempotency_key(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class IdempotencyStore:
    """같은 키는 한 번만 실행하고, 이후 호출은 저장된 결과를 재생(replay)한다."""

    def __init__(self):
        self._seen = {}

    def issue_once(self, key, fn):
        if key in self._seen:
            return self._seen[key], True  # replay (중복 아님)
        result = fn()
        self._seen[key] = result
        return result, False

# -*- coding: utf-8 -*-
"""멱등 처리 — idempotency_key로 중복 가입을 차단한다."""
import hashlib
import json


def idempotency_key(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class IdempotencyStore:
    def __init__(self):
        self._seen = {}

    def issue_once(self, key, fn):
        if key in self._seen:
            return self._seen[key], True
        result = fn()
        self._seen[key] = result
        return result, False

# -*- coding: utf-8 -*-
"""멱등 처리: 동일 key(order_id 등)의 재실행은 최초 결과를 그대로 반환한다."""


class IdempotencyStore:
    def __init__(self):
        self._seen = {}

    def issue_once(self, key, fn):
        if key in self._seen:
            return self._seen[key], True
        result = fn()
        self._seen[key] = result
        return result, False

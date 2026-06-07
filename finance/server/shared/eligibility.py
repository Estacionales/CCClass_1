# -*- coding: utf-8 -*-
"""자격 판정 — 예외 조건 충족 여부로 발급 자격을 결정 (AC-3 가드레일)."""
from server.shared import rules

required_documents = rules.required_documents


class EligibilityPolicy:
    """사용자별로 충족한 예외 조건을 기록하고, 발급 자격을 판정한다.

    satisfied: {(user_id, 예외조건)} 집합.
    """

    def __init__(self):
        self._satisfied = set()

    def satisfy(self, user_id, condition):
        self._satisfied.add((user_id, condition))

    def is_eligible(self, user_id, minwon_type):
        for cond in rules.exceptions_of(minwon_type):
            if (user_id, cond) not in self._satisfied:
                return False
        return True

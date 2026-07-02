# -*- coding: utf-8 -*-
"""투데이: 하루 한 번만 등록. 같은 날짜 재요청은 멱등(already)으로 응답한다.

날짜는 호출자가 주입한다(day: "YYYY-MM-DD" 문자열) - 실시간 비의존, 결정적 테스트.
"""
from dataclasses import dataclass


@dataclass
class TodayResult:
    status: str  # recorded | already
    reason: str = ""


class TodayService:
    def __init__(self):
        self._records = {}  # user -> set(day)

    def check_in(self, user, day):
        seen = self._records.setdefault(user, set())
        if day in seen:
            return TodayResult("already", "already_checked_in")
        seen.add(day)
        return TodayResult("recorded", "ok")

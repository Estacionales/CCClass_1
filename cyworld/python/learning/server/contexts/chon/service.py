# -*- coding: utf-8 -*-
"""일촌: 신청(request) → 수락(accept). 양방향 관계로 성립한다.

AC-1~AC-7 전부 구현: 신청·수락·재신청 멱등·TTL(24h) 만료·정원(750)·파일촌(해제)·일촌평.
`clock`을 주입해 TTL을 결정적으로 테스트한다(실시간 비의존).
"""
import time
from dataclasses import dataclass

DEFAULT_TTL_S = 86400  # 24시간
DEFAULT_MAX_CHON = 750


@dataclass
class ChonResult:
    status: str  # pending | accepted | rejected | removed | written
    reason: str = ""


class ChonService:
    def __init__(self, *, ttl_s=DEFAULT_TTL_S, max_chon=DEFAULT_MAX_CHON, clock=None):
        self.ttl_s = ttl_s
        self.max_chon = max_chon
        self._clock = clock or time.time
        self._requests = {}  # (from_user, to_user) -> {"status", "issued"}
        self._chon = {}  # user -> set(chon 상대)
        self._chonpyeong = {}  # (from_user, to_user) -> text

    def _is_expired(self, rec):
        return self._clock() - rec["issued"] > self.ttl_s

    def request(self, from_user, to_user):
        if self.is_chon(from_user, to_user):
            return ChonResult("accepted", "already_chon")

        key = (from_user, to_user)
        rec = self._requests.get(key)
        if rec and rec["status"] == "pending" and not self._is_expired(rec):
            return ChonResult("pending", "already_requested")

        self._requests[key] = {"status": "pending", "issued": self._clock()}
        return ChonResult("pending", "ok")

    def accept(self, from_user, to_user):
        """to_user가 from_user의 신청을 수락한다."""
        key = (from_user, to_user)
        rec = self._requests.get(key)
        if rec is None or rec["status"] != "pending":
            return ChonResult("rejected", "no_pending_request")
        if self._is_expired(rec):
            rec["status"] = "expired"
            return ChonResult("rejected", "expired")
        if (len(self._chon.get(from_user, set())) >= self.max_chon
                or len(self._chon.get(to_user, set())) >= self.max_chon):
            return ChonResult("rejected", "capacity_exceeded")

        rec["status"] = "accepted"
        self._chon.setdefault(from_user, set()).add(to_user)
        self._chon.setdefault(to_user, set()).add(from_user)
        return ChonResult("accepted", "ok")

    def unchon(self, user_a, user_b):
        """파일촌: 양쪽 목록에서 동시에 관계를 제거한다."""
        if not self.is_chon(user_a, user_b):
            return ChonResult("rejected", "not_chon")
        self._chon[user_a].discard(user_b)
        self._chon[user_b].discard(user_a)
        return ChonResult("removed", "ok")

    def write_chonpyeong(self, from_user, to_user, text):
        if not self.is_chon(from_user, to_user):
            return ChonResult("rejected", "not_chon")
        self._chonpyeong[(from_user, to_user)] = text
        return ChonResult("written", "ok")

    def is_chon(self, user_a, user_b):
        return user_b in self._chon.get(user_a, set())

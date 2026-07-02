# -*- coding: utf-8 -*-
"""미니홈피: 자동 생성, 다이어리 공개범위 접근제어, 방문자수, 스킨/BGM 적용.

일촌공개 접근제어는 주입된 `chon`(ChonService.is_chon)에, 스킨/BGM 적용은 주입된
`acorn`(AcornService.inventory)에 의존한다 - 04_data 없이 컨텍스트 간 직접 참조로 연결.
"""
import time
from dataclasses import dataclass

VISIT_DEDUP_WINDOW_S = 86400  # 24시간
DAY_S = 86400


@dataclass
class MinihomepyResult:
    status: str
    reason: str = ""


@dataclass
class DiaryReadResult:
    status: str  # ok | rejected
    reason: str = ""
    content: str = ""


class MinihomepyService:
    def __init__(self, chon=None, acorn=None, clock=None):
        self.chon = chon
        self.acorn = acorn
        self._clock = clock or time.time
        self.homepages = {}  # owner -> True
        self.applied_items = {}  # owner -> item_id
        self.visitor_counts = {}  # owner -> int(누적)
        self._visits = {}  # owner -> {visitor: last_ts}
        self._visit_today = {}  # owner -> {"day": int, "count": int}
        self._posts = {}  # post_id -> dict
        self._post_seq = 0
        self.profiles = {}  # owner -> {"nickname", "mood", "status_message"}

    def create_for_user(self, user):
        if user in self.homepages:
            return MinihomepyResult("exists", "already_created")
        self.homepages[user] = True
        return MinihomepyResult("created", "ok")

    def set_profile(self, owner, *, nickname=None, mood=None, status_message=None):
        profile = self.profiles.setdefault(
            owner, {"nickname": owner, "mood": "", "status_message": ""})
        if nickname is not None:
            profile["nickname"] = nickname
        if mood is not None:
            profile["mood"] = mood
        if status_message is not None:
            profile["status_message"] = status_message
        return profile

    def get_profile(self, owner):
        return self.profiles.get(owner, {"nickname": owner, "mood": "", "status_message": ""})

    def diary_count(self, owner):
        return sum(1 for p in self._posts.values() if p["owner"] == owner)

    def write_diary(self, owner, author, content, visibility):
        """visibility: public | chon | private"""
        self._post_seq += 1
        post_id = self._post_seq
        self._posts[post_id] = {
            "owner": owner, "author": author,
            "content": content, "visibility": visibility,
        }
        return post_id

    def read_diary(self, post_id, viewer):
        post = self._posts.get(post_id)
        if post is None:
            return DiaryReadResult("rejected", "not_found")

        visibility = post["visibility"]
        if viewer == post["author"]:
            return DiaryReadResult("ok", "ok", content=post["content"])
        if visibility == "private":
            return DiaryReadResult("rejected", "private")
        if visibility == "chon":
            is_chon = self.chon.is_chon(post["author"], viewer) if self.chon else False
            if not is_chon:
                return DiaryReadResult("rejected", "chon_only")
        return DiaryReadResult("ok", "ok", content=post["content"])

    def list_diary(self, owner, viewer):
        """viewer가 조회 가능한 owner의 다이어리를 작성순으로 반환한다."""
        entries = []
        for post_id in sorted(pid for pid, p in self._posts.items() if p["owner"] == owner):
            r = self.read_diary(post_id, viewer)
            if r.status == "ok":
                entries.append({
                    "post_id": post_id,
                    "visibility": self._posts[post_id]["visibility"],
                    "content": r.content,
                })
        return entries

    def visit(self, owner, visitor):
        if owner == visitor:
            return MinihomepyResult("skipped", "self_visit")
        now = self._clock()
        seen = self._visits.setdefault(owner, {})
        last = seen.get(visitor)
        if last is not None and now - last < VISIT_DEDUP_WINDOW_S:
            return MinihomepyResult("skipped", "duplicate_within_24h")
        seen[visitor] = now
        self.visitor_counts[owner] = self.visitor_counts.get(owner, 0) + 1
        self._bump_today(owner, now)
        return MinihomepyResult("counted", "ok")

    def _bump_today(self, owner, now):
        day = int(now // DAY_S)
        bucket = self._visit_today.get(owner)
        if bucket is None or bucket["day"] != day:
            bucket = {"day": day, "count": 0}
        bucket["count"] += 1
        self._visit_today[owner] = bucket

    def visits_today(self, owner):
        day = int(self._clock() // DAY_S)
        bucket = self._visit_today.get(owner)
        if bucket is None or bucket["day"] != day:
            return 0
        return bucket["count"]

    def apply_item(self, user, item_id):
        owned = self.acorn.inventory.get(user, set()) if self.acorn else set()
        if item_id not in owned:
            return MinihomepyResult("rejected", "not_owned")
        self.applied_items[user] = item_id
        return MinihomepyResult("applied", "ok")

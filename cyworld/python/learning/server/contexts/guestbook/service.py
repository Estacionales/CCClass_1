# -*- coding: utf-8 -*-
"""방명록: 작성(시간순)·삭제 권한·비밀글 마스킹·주인 답글 1개 제한."""
import time
from dataclasses import dataclass


@dataclass
class GuestbookResult:
    status: str
    reason: str = ""


@dataclass
class GuestbookReadResult:
    status: str  # ok | rejected
    reason: str = ""
    content: str = ""
    masked: bool = False
    author: str = ""
    reply: str = None


class GuestbookService:
    MASK = "***"

    def __init__(self, clock=None):
        self._clock = clock or time.time
        self._messages = {}  # msg_id -> dict
        self._seq = 0

    def post(self, owner, author, content, secret=False):
        self._seq += 1
        msg_id = self._seq
        self._messages[msg_id] = {
            "owner": owner, "author": author, "content": content,
            "secret": secret, "ts": self._clock(), "reply": None,
        }
        return msg_id

    def list_messages(self, owner):
        """시간순(오름차순) 메시지 id 목록."""
        items = [(mid, m) for mid, m in self._messages.items() if m["owner"] == owner]
        items.sort(key=lambda kv: kv[1]["ts"])
        return [mid for mid, _ in items]

    def count(self, owner):
        return sum(1 for m in self._messages.values() if m["owner"] == owner)

    def read(self, msg_id, viewer):
        m = self._messages.get(msg_id)
        if m is None:
            return GuestbookReadResult("rejected", "not_found")
        if m["secret"] and viewer not in (m["owner"], m["author"]):
            return GuestbookReadResult("ok", content=self.MASK, masked=True,
                                        author=m["author"], reply=m["reply"])
        return GuestbookReadResult("ok", content=m["content"], masked=False,
                                    author=m["author"], reply=m["reply"])

    def delete(self, msg_id, requester):
        m = self._messages.get(msg_id)
        if m is None:
            return GuestbookResult("rejected", "not_found")
        if requester not in (m["owner"], m["author"]):
            return GuestbookResult("rejected", "not_authorized")
        del self._messages[msg_id]
        return GuestbookResult("deleted", "ok")

    def reply(self, msg_id, owner, content):
        m = self._messages.get(msg_id)
        if m is None:
            return GuestbookResult("rejected", "not_found")
        if owner != m["owner"]:
            return GuestbookResult("rejected", "not_owner")
        if m["reply"] is not None:
            return GuestbookResult("rejected", "reply_exists")
        m["reply"] = content
        return GuestbookResult("replied", "ok")

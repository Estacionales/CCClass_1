# -*- coding: utf-8 -*-
"""버디버디 메신저: 버디(친구) 요청·수락·거절, 1:1 채팅, 상태, 안읽음.

AC-1~AC-8 전부 구현: 요청 PENDING · 수락(양방향)·요청 제거 · 재요청 멱등 ·
거절(재요청 허용) · 비버디 전송 거부 · 대화 시간순 대칭 조회 ·
상태(온라인/자리비움/오프라인, 버디 전용 공개) · 안읽음 큐잉 + 열람 시 읽음 처리.
`clock`을 주입해 메시지 시각을 결정적으로 테스트한다(실시간 비의존).
"""
import time
from dataclasses import dataclass

PRESENCE_STATES = ("online", "away", "offline")


@dataclass
class BuddyResult:
    status: str  # pending | accepted | rejected
    reason: str = ""


@dataclass
class MessageSendResult:
    status: str  # sent | rejected
    reason: str = ""
    message_id: int = None


@dataclass
class Message:
    id: int
    sender: str
    content: str
    ts: float
    read: bool = False


class BuddyService:
    def __init__(self, clock=None):
        self._clock = clock or time.time
        self._requests = {}  # (from_user, to_user) -> "pending"
        self._buddies = {}  # user -> set(buddy)
        self._conversations = {}  # frozenset({a,b}) -> list[Message]
        self._presence = {}  # user -> status
        self._seq = 0

    # --- 버디 관계 ---
    def request(self, from_user, to_user):
        if self.is_buddy(from_user, to_user):
            return BuddyResult("accepted", "already_buddy")
        if self._requests.get((from_user, to_user)) == "pending":
            return BuddyResult("pending", "already_requested")
        self._requests[(from_user, to_user)] = "pending"
        return BuddyResult("pending", "ok")

    def accept(self, from_user, to_user):
        """to_user가 from_user의 요청을 수락한다."""
        if self._requests.get((from_user, to_user)) != "pending":
            return BuddyResult("rejected", "no_pending_request")
        del self._requests[(from_user, to_user)]
        self._buddies.setdefault(from_user, set()).add(to_user)
        self._buddies.setdefault(to_user, set()).add(from_user)
        return BuddyResult("accepted", "ok")

    def reject(self, from_user, to_user):
        """to_user가 from_user의 요청을 거절한다. 이후 재요청은 다시 가능하다."""
        if self._requests.get((from_user, to_user)) != "pending":
            return BuddyResult("rejected", "no_pending_request")
        del self._requests[(from_user, to_user)]
        return BuddyResult("rejected", "ok")

    def is_buddy(self, user_a, user_b):
        return user_b in self._buddies.get(user_a, set())

    def pending_requests_for(self, user):
        """user가 받은 PENDING 요청의 발신자 목록(정렬됨)."""
        return sorted(f for (f, t), status in self._requests.items()
                      if t == user and status == "pending")

    def buddies_of(self, user):
        return sorted(self._buddies.get(user, set()))

    # --- 상태(presence) ---
    def set_presence(self, user, status):
        if status not in PRESENCE_STATES:
            raise ValueError(f"invalid presence: {status}")
        self._presence[user] = status

    def get_presence(self, user, viewer):
        """버디이거나 본인일 때만 실제 상태를 노출, 그 외는 'unknown'."""
        if user == viewer or self.is_buddy(user, viewer):
            return self._presence.get(user, "offline")
        return "unknown"

    # --- 메시징 ---
    def _conv_key(self, user_a, user_b):
        return frozenset((user_a, user_b))

    def send_message(self, sender, recipient, content):
        if not self.is_buddy(sender, recipient):
            return MessageSendResult("rejected", "not_buddy")
        self._seq += 1
        msg = Message(id=self._seq, sender=sender, content=content, ts=self._clock())
        self._conversations.setdefault(self._conv_key(sender, recipient), []).append(msg)
        return MessageSendResult("sent", "ok", message_id=msg.id)

    def get_conversation(self, user_a, user_b, since_id=0):
        """user_a·user_b 대화를 시간순(id 오름차순)으로, since_id보다 큰 것만 반환."""
        msgs = self._conversations.get(self._conv_key(user_a, user_b), [])
        return [m for m in msgs if m.id > since_id]

    def unread_count(self, owner, buddy):
        """owner 기준 buddy가 보낸 메시지 중 안읽음 개수."""
        msgs = self._conversations.get(self._conv_key(owner, buddy), [])
        return sum(1 for m in msgs if m.sender == buddy and not m.read)

    def mark_read(self, owner, buddy):
        """owner가 buddy와의 대화를 열람: buddy가 보낸 안읽은 메시지를 읽음 처리."""
        msgs = self._conversations.get(self._conv_key(owner, buddy), [])
        for m in msgs:
            if m.sender == buddy:
                m.read = True

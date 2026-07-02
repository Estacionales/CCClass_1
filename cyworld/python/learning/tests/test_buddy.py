# -*- coding: utf-8 -*-
"""버디버디 메신저: 요청→수락/거절, 멱등, 비버디 전송 거부, 대화, 상태, 안읽음."""


def test_request_then_accept(buddy):
    r1 = buddy.request("u1", "u2")
    assert r1.status == "pending"

    r2 = buddy.accept("u1", "u2")
    assert r2.status == "accepted"
    assert buddy.is_buddy("u1", "u2")
    assert buddy.is_buddy("u2", "u1")  # 양방향


def test_accept_without_request_rejected(buddy):
    r = buddy.accept("u1", "u2")
    assert r.status == "rejected" and r.reason == "no_pending_request"


def test_request_idempotent_while_pending(buddy):
    buddy.request("u1", "u2")
    r2 = buddy.request("u1", "u2")  # 재요청
    assert r2.status == "pending" and r2.reason == "already_requested"


def test_request_already_buddy_idempotent(buddy):
    buddy.request("u1", "u2")
    buddy.accept("u1", "u2")
    r = buddy.request("u1", "u2")  # 이미 버디인데 재요청
    assert r.status == "accepted" and r.reason == "already_buddy"


def test_reject_discards_and_allows_reask(buddy):
    buddy.request("u1", "u2")
    r_reject = buddy.reject("u1", "u2")
    assert r_reject.status == "rejected" and r_reject.reason == "ok"
    assert not buddy.is_buddy("u1", "u2")

    r_reask = buddy.request("u1", "u2")  # 거절 이후 재요청 허용
    assert r_reask.status == "pending" and r_reask.reason == "ok"

    r_ok = buddy.accept("u1", "u2")
    assert r_ok.status == "accepted"


def test_send_message_requires_buddy(buddy):
    r = buddy.send_message("u1", "u2", "안녕!")
    assert r.status == "rejected" and r.reason == "not_buddy"
    assert buddy.get_conversation("u1", "u2") == []


def test_send_message_stored_ordered_and_symmetric(buddy):
    buddy.request("u1", "u2")
    buddy.accept("u1", "u2")

    buddy.test_clock["t"] = 1000.0
    buddy.send_message("u1", "u2", "안녕!")
    buddy.test_clock["t"] = 1001.0
    buddy.send_message("u2", "u1", "오 반가워~")

    conv_from_u1 = buddy.get_conversation("u1", "u2")
    conv_from_u2 = buddy.get_conversation("u2", "u1")
    assert [m.content for m in conv_from_u1] == ["안녕!", "오 반가워~"]
    assert [m.content for m in conv_from_u2] == ["안녕!", "오 반가워~"]  # 대칭 조회
    assert conv_from_u1[0].ts < conv_from_u1[1].ts  # 시간순


def test_get_conversation_since_id_returns_only_new_messages(buddy):
    buddy.request("u1", "u2")
    buddy.accept("u1", "u2")
    buddy.send_message("u1", "u2", "1번")
    r2 = buddy.send_message("u2", "u1", "2번")
    buddy.send_message("u1", "u2", "3번")

    newer = buddy.get_conversation("u1", "u2", since_id=r2.message_id)
    assert [m.content for m in newer] == ["3번"]


def test_presence_visible_to_buddy_only(buddy):
    buddy.request("u1", "u2")
    buddy.accept("u1", "u2")
    buddy.set_presence("u1", "online")

    assert buddy.get_presence("u1", "u2") == "online"  # 버디에게 공개
    assert buddy.get_presence("u1", "u1") == "online"  # 본인
    assert buddy.get_presence("u1", "stranger") == "unknown"  # 비버디에는 비공개


def test_unread_count_and_mark_read(buddy):
    buddy.request("u1", "u2")
    buddy.accept("u1", "u2")
    buddy.send_message("u2", "u1", "1번")
    buddy.send_message("u2", "u1", "2번")

    assert buddy.unread_count("u1", "u2") == 2

    buddy.mark_read("u1", "u2")  # u1이 u2와의 대화를 열람
    assert buddy.unread_count("u1", "u2") == 0
    # u2 쪽 안읽음(자기 자신이 보낸 메시지 기준)에는 영향 없음
    assert buddy.unread_count("u2", "u1") == 0

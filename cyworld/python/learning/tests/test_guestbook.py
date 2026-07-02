# -*- coding: utf-8 -*-
"""방명록: 작성(시간순), 삭제 권한, 비밀글 마스킹, 주인 답글 1개 제한."""


def test_post_message_ordered(guestbook):
    svc, clock = guestbook
    m1 = svc.post("owner", "visitor1", "안녕")
    clock["t"] += 1
    m2 = svc.post("owner", "visitor2", "방가")
    assert svc.list_messages("owner") == [m1, m2]


def test_delete_permission(guestbook):
    svc, _ = guestbook
    m1 = svc.post("owner", "visitor1", "메시지1")
    m2 = svc.post("owner", "visitor2", "메시지2")

    r_stranger = svc.delete(m1, "stranger")
    assert r_stranger.status == "rejected" and r_stranger.reason == "not_authorized"

    r_author = svc.delete(m1, "visitor1")  # 작성자 본인
    assert r_author.status == "deleted"

    r_owner = svc.delete(m2, "owner")  # 방명록 주인
    assert r_owner.status == "deleted"


def test_secret_message_masking(guestbook):
    svc, _ = guestbook
    m1 = svc.post("owner", "visitor1", "비밀 메시지", secret=True)

    r_stranger = svc.read(m1, "stranger")
    assert r_stranger.masked is True and r_stranger.content == "***"

    r_owner = svc.read(m1, "owner")
    assert r_owner.masked is False and r_owner.content == "비밀 메시지"

    r_author = svc.read(m1, "visitor1")
    assert r_author.masked is False and r_author.content == "비밀 메시지"


def test_count_returns_owner_message_total(guestbook):
    svc, _ = guestbook
    svc.post("owner", "visitor1", "메시지1")
    svc.post("owner", "visitor2", "메시지2")
    svc.post("other-owner", "visitor1", "다른 사람 방명록")
    assert svc.count("owner") == 2
    assert svc.count("other-owner") == 1
    assert svc.count("nobody") == 0


def test_owner_reply_limit_one(guestbook):
    svc, _ = guestbook
    m1 = svc.post("owner", "visitor1", "메시지")

    r_stranger = svc.reply(m1, "stranger", "답글")
    assert r_stranger.status == "rejected" and r_stranger.reason == "not_owner"

    r1 = svc.reply(m1, "owner", "첫 답글")
    assert r1.status == "replied"

    r2 = svc.reply(m1, "owner", "두번째 답글")
    assert r2.status == "rejected" and r2.reason == "reply_exists"

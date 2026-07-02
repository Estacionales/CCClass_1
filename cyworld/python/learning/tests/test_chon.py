# -*- coding: utf-8 -*-
"""일촌: 신청 → 수락, 재신청 멱등, TTL 만료, 정원(750), 파일촌, 일촌평."""


def test_request_then_accept(chon):
    r1 = chon.request("u1", "u2")
    assert r1.status == "pending"

    r2 = chon.accept("u1", "u2")
    assert r2.status == "accepted"
    assert chon.is_chon("u1", "u2")
    assert chon.is_chon("u2", "u1")  # 양방향


def test_accept_without_request_rejected(chon):
    r = chon.accept("u1", "u2")
    assert r.status == "rejected" and r.reason == "no_pending_request"


def test_request_idempotent_while_pending(chon):
    chon.request("u1", "u2")
    r2 = chon.request("u1", "u2")  # 재신청
    assert r2.status == "pending" and r2.reason == "already_requested"


def test_request_already_chon(chon):
    chon.request("u1", "u2")
    chon.accept("u1", "u2")
    r = chon.request("u1", "u2")  # 이미 일촌인데 재신청
    assert r.status == "accepted" and r.reason == "already_chon"


def test_request_expiry_allows_reaccept(chon):
    chon.request("u1", "u2")
    chon.test_clock["t"] += 86401  # TTL(24h) 초과

    r_accept = chon.accept("u1", "u2")  # 만료된 요청 수락 시도
    assert r_accept.status == "rejected" and r_accept.reason == "expired"

    r_reask = chon.request("u1", "u2")  # 만료 이후 재신청은 허용
    assert r_reask.status == "pending" and r_reask.reason == "ok"

    r_ok = chon.accept("u1", "u2")
    assert r_ok.status == "accepted"


def test_request_not_expired_within_ttl(chon):
    chon.request("u1", "u2")
    chon.test_clock["t"] += 86399  # TTL(24h) 이내
    r = chon.request("u1", "u2")  # 아직 유효 → 멱등
    assert r.status == "pending" and r.reason == "already_requested"


def test_chon_capacity_750_rejects_accept(chon):
    chon._chon["u1"] = {f"filler-{i}" for i in range(750)}  # white-box: 정원 750 세팅
    chon.request("u1", "u2")
    r = chon.accept("u1", "u2")
    assert r.status == "rejected" and r.reason == "capacity_exceeded"
    assert not chon.is_chon("u1", "u2")


def test_unchon_removes_both_sides(chon):
    chon.request("u1", "u2")
    chon.accept("u1", "u2")

    r = chon.unchon("u1", "u2")
    assert r.status == "removed"
    assert not chon.is_chon("u1", "u2")
    assert not chon.is_chon("u2", "u1")


def test_unchon_when_not_chon_rejected(chon):
    r = chon.unchon("u1", "u2")
    assert r.status == "rejected" and r.reason == "not_chon"


def test_chonpyeong_requires_chon(chon):
    r_denied = chon.write_chonpyeong("u1", "u2", "우리 친해요")
    assert r_denied.status == "rejected" and r_denied.reason == "not_chon"

    chon.request("u1", "u2")
    chon.accept("u1", "u2")
    r_ok = chon.write_chonpyeong("u1", "u2", "우리 친해요")
    assert r_ok.status == "written"

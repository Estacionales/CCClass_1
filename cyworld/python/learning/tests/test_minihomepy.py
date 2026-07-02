# -*- coding: utf-8 -*-
"""미니홈피: 자동 생성, 다이어리 공개범위, 방문자수, 스킨/BGM 적용."""


def test_signup_creates_homepy(minihomepy):
    svc, _ = minihomepy
    r = svc.create_for_user("u1")
    assert r.status == "created"
    assert "u1" in svc.homepages


def test_diary_visibility_private(minihomepy):
    svc, _ = minihomepy
    post_id = svc.write_diary("u1", "u1", "비밀 일기", "private")
    assert svc.read_diary(post_id, "u1").status == "ok"  # 본인
    r = svc.read_diary(post_id, "u2")  # 타인
    assert r.status == "rejected" and r.reason == "private"


def test_diary_visibility_public(minihomepy):
    svc, _ = minihomepy
    post_id = svc.write_diary("u1", "u1", "공개 일기", "public")
    r = svc.read_diary(post_id, "stranger")
    assert r.status == "ok" and r.content == "공개 일기"


def test_diary_visibility_chon_only(minihomepy):
    svc, _ = minihomepy
    post_id = svc.write_diary("u1", "u1", "일촌공개 일기", "chon")

    r_stranger = svc.read_diary(post_id, "u2")
    assert r_stranger.status == "rejected" and r_stranger.reason == "chon_only"

    svc.chon.request("u1", "u2")
    svc.chon.accept("u1", "u2")
    r_chon = svc.read_diary(post_id, "u2")
    assert r_chon.status == "ok"


def test_visitor_count_dedup_24h(minihomepy):
    svc, clock = minihomepy
    assert svc.visit("u1", "u1").reason == "self_visit"  # 본인 방문 제외
    assert svc.visitor_counts.get("u1", 0) == 0

    assert svc.visit("u1", "u2").status == "counted"
    assert svc.visitor_counts["u1"] == 1

    assert svc.visit("u1", "u2").reason == "duplicate_within_24h"  # 24시간 내 재방문
    assert svc.visitor_counts["u1"] == 1

    clock["t"] += 86400  # 24시간 경과
    assert svc.visit("u1", "u2").status == "counted"
    assert svc.visitor_counts["u1"] == 2


def test_skin_bgm_requires_inventory(minihomepy):
    svc, _ = minihomepy
    r_denied = svc.apply_item("u1", "skin-1")
    assert r_denied.status == "rejected" and r_denied.reason == "not_owned"

    svc.acorn.charge("u1", 100, order_id="pay-1")
    svc.acorn.purchase("u1", "skin-1", 100, order_id="order-1")
    r_ok = svc.apply_item("u1", "skin-1")
    assert r_ok.status == "applied"
    assert svc.applied_items["u1"] == "skin-1"


def test_set_and_get_profile(minihomepy):
    svc, _ = minihomepy
    default = svc.get_profile("u1")
    assert default["nickname"] == "u1" and default["status_message"] == ""

    svc.set_profile("u1", nickname="유나", mood="감성", status_message="오늘도 화이팅")
    updated = svc.get_profile("u1")
    assert updated == {"nickname": "유나", "mood": "감성", "status_message": "오늘도 화이팅"}


def test_diary_count_counts_all_regardless_of_visibility():
    from server.contexts.minihomepy.service import MinihomepyService
    svc = MinihomepyService()
    svc.write_diary("u1", "u1", "글1", "public")
    svc.write_diary("u1", "u1", "글2", "private")
    assert svc.diary_count("u1") == 2
    assert svc.diary_count("u2") == 0


def test_visits_today_resets_on_new_day(minihomepy):
    svc, clock = minihomepy
    assert svc.visits_today("u1") == 0

    svc.visit("u1", "v1")
    svc.visit("u1", "v2")
    assert svc.visits_today("u1") == 2
    assert svc.visitor_counts["u1"] == 2  # 누적 TOTAL도 함께 증가

    clock["t"] += 86400  # 다음 날
    assert svc.visits_today("u1") == 0  # 오늘 카운트는 리셋
    svc.visit("u1", "v3")
    assert svc.visits_today("u1") == 1
    assert svc.visitor_counts["u1"] == 3  # TOTAL은 계속 누적

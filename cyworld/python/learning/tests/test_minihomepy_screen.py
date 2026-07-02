# -*- coding: utf-8 -*-
"""미니홈피 화면 렌더(순수 함수): 프레임/사이드바/통계바/탭/다이어리/방명록, XSS 이스케이프."""
from server.contexts.minihomepy import screens


def test_render_stats_bar():
    html = screens.render_stats_bar(today_visits=7, total_visits=87363)
    assert "TODAY 7" in html
    assert "TOTAL <b class=\"total\">87,363</b>" in html


def test_render_profile_sidebar():
    html = screens.render_profile_sidebar(
        owner="yuna", nickname="유나", mood="감성", status_message="오늘도 화이팅")
    assert "TODAY IS... 감성" in html
    assert "오늘도 화이팅" in html
    assert "유나 파도타기" in html

    empty_html = screens.render_profile_sidebar(
        owner="yuna", nickname="유나", mood="", status_message="")
    assert "아직 등록된 상태메시지가 없습니다" in empty_html


def test_render_diary_visibility():
    entries = [
        {"post_id": 1, "visibility": "public", "content": "공개글"},
        {"post_id": 2, "visibility": "chon", "content": "일촌공개글"},
    ]
    html = screens.render_diary(entries)
    assert "[전체공개]" in html and "공개글" in html
    assert "[일촌공개]" in html and "일촌공개글" in html

    empty_html = screens.render_diary([])
    assert "작성된 다이어리가 없습니다" in empty_html


def test_render_guestbook():
    entries = [
        {"author": "minsu", "content": "안녕", "masked": False, "reply": "고마워"},
        {"author": "stranger", "content": "***", "masked": True, "reply": None},
    ]
    html = screens.render_guestbook("yuna", entries, viewer="minsu")
    assert "minsu" in html and "안녕" in html
    assert "주인 답글: 고마워" in html
    assert 'class="secret">***' in html
    assert 'name="viewer" value="minsu"' in html  # 리다이렉트용 hidden field


def test_render_friends_say_hides_masked_entries():
    entries = [
        {"author": "minsu", "content": "놀러왔어요", "masked": False, "reply": None},
        {"author": "stranger", "content": "***", "masked": True, "reply": None},
    ]
    html = screens.render_friends_say(entries)
    assert "놀러왔어요" in html
    assert "***" not in html

    empty_html = screens.render_friends_say([])
    assert "아직 친구들의 한마디가 없습니다" in empty_html


def test_render_nav_tabs_marks_active():
    html = screens.render_nav_tabs("yuna", active="home")
    assert 'class="active"' in html
    assert "홈" in html and "다이어리" in html and "방명록" in html
    assert 'class="disabled"' in html  # 사진첩(미구현)


def test_render_escapes_user_content():
    xss = '<script>alert(1)</script>'
    diary_html = screens.render_diary([{"post_id": 1, "visibility": "public", "content": xss}])
    assert "<script>" not in diary_html
    assert "&lt;script&gt;" in diary_html

    guestbook_html = screens.render_guestbook(
        "yuna", [{"author": xss, "content": xss, "masked": False, "reply": None}])
    assert "<script>" not in guestbook_html
    assert "&lt;script&gt;" in guestbook_html

    sidebar_html = screens.render_profile_sidebar(
        owner="yuna", nickname=xss, mood=xss, status_message=xss)
    assert "<script>" not in sidebar_html


def test_render_page_assembles_sections():
    html = screens.render_page(
        owner="yuna", viewer="minsu", nickname="유나", mood="감성",
        status_message="오늘도 화이팅", applied_item="skin-pink",
        today_visits=3, total_visits=87363, diary_count=2, guestbook_count=1,
        diary_entries=[{"post_id": 1, "visibility": "public", "content": "hi"}],
        guestbook_entries=[],
    )
    assert "<title>yuna의 미니홈피</title>" in html
    assert "유나의 추억 상자" in html
    assert "다이어리" in html and "방명록" in html and "Miniroom" in html
    assert "What Friends say" in html
    assert 'class="frame"' in html  # 바인더 프레임

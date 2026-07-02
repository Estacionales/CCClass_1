# -*- coding: utf-8 -*-
"""버디버디 메신저 화면 렌더(순수 함수): 리스트/채팅/상태점/안읽음 배지, XSS 이스케이프."""
from server.contexts.buddy import screens


def test_render_buddy_list():
    html = screens.render_buddy_list(
        user="yuna", my_presence="online",
        pending_senders=["stranger"],
        buddies=[{"name": "minsu", "presence": "online", "unread": 2}],
    )
    assert "받은 버디 요청" in html
    assert "stranger" in html and "수락" in html and "거절" in html
    assert "minsu" in html
    assert '<span class="unread-badge">2</span>' in html
    assert 'action="/messenger/yuna/request"' in html
    assert 'selected' in html  # 현재 상태(online) selected 옵션


def test_render_buddy_list_empty_states():
    html = screens.render_buddy_list(
        user="yuna", my_presence="offline", pending_senders=[], buddies=[])
    assert "받은 버디 요청이 없습니다" in html
    assert "아직 버디가 없습니다" in html


def test_render_chat():
    messages = [
        {"sender": "minsu", "content": "안녕!", "ts": 1000.0},
        {"sender": "yuna", "content": "반가워~", "ts": 1001.0},
    ]
    html = screens.render_chat(
        owner="yuna", buddy="minsu", buddy_presence="online",
        messages=messages, last_id=2)
    assert 'class="msg theirs"' in html  # minsu(상대)가 보낸 메시지
    assert 'class="msg mine"' in html  # yuna(본인)가 보낸 메시지
    assert "안녕!" in html and "반가워~" in html
    assert 'lastId=2' in html  # 폴링 시작점


def test_render_chat_empty_state():
    html = screens.render_chat(
        owner="yuna", buddy="minsu", buddy_presence="offline",
        messages=[], last_id=0)
    assert "아직 대화가 없습니다" in html


def test_render_escapes_user_content():
    xss = '<script>alert(1)</script>'
    list_html = screens.render_buddy_list(
        user="yuna", my_presence="online",
        pending_senders=[xss], buddies=[{"name": xss, "presence": "online", "unread": 0}])
    assert "<script>" not in list_html
    assert "&lt;script&gt;" in list_html

    chat_html = screens.render_chat(
        owner="yuna", buddy="minsu", buddy_presence="online",
        messages=[{"sender": xss, "content": xss, "ts": 1000.0}], last_id=1)
    assert "<script>alert(1)</script>" not in chat_html
    assert "&lt;script&gt;" in chat_html

# -*- coding: utf-8 -*-
"""미니홈피 WSGI 앱: 실제 소켓 없이 WSGI 콜러블을 직접 호출해 라우팅을 검증한다."""
import json
from io import BytesIO
from urllib.parse import urlencode

from server.web.app import build_services, make_app, seed_demo_data


def _call(app, method, path, query="", body=""):
    body_bytes = body if isinstance(body, bytes) else body.encode("utf-8")
    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": query,
        "CONTENT_LENGTH": str(len(body_bytes)),
        "wsgi.input": BytesIO(body_bytes),
    }
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = headers

    chunks = app(environ, start_response)
    return captured["status"], dict(captured["headers"]), b"".join(chunks).decode("utf-8")


def _seeded_app():
    chon, acorn, homepy, guestbook, buddy = build_services()
    seed_demo_data(chon, acorn, homepy, guestbook, buddy)
    return make_app(chon, acorn, homepy, guestbook, buddy), homepy, guestbook, buddy


def test_index_lists_seeded_owners():
    app, _, _, _ = _seeded_app()
    status, _, body = _call(app, "GET", "/")
    assert status == "200 OK"
    assert "/minihomepy/yuna" in body


def test_minihomepy_page_respects_visibility_by_viewer():
    app, _, _, _ = _seeded_app()

    _, _, as_stranger = _call(app, "GET", "/minihomepy/yuna", query="viewer=stranger")
    assert "안녕하세요" in as_stranger  # 전체공개
    assert "일촌에게만 보이는" not in as_stranger  # 일촌 아님
    assert "비밀 일기" not in as_stranger  # 비공개

    _, _, as_chon = _call(app, "GET", "/minihomepy/yuna", query="viewer=minsu")
    assert "일촌에게만 보이는" in as_chon  # minsu는 yuna와 일촌(시드 데이터)
    assert "비밀 일기" not in as_chon


def test_minihomepy_page_unknown_owner_404():
    app, _, _, _ = _seeded_app()
    status, _, _ = _call(app, "GET", "/minihomepy/nobody", query="viewer=guest")
    assert status == "404 Not Found"


def test_visit_increments_visitor_count_excluding_self():
    app, homepy, _, _ = _seeded_app()
    _call(app, "GET", "/minihomepy/yuna", query="viewer=yuna")  # 본인 방문
    assert homepy.visitor_counts.get("yuna", 0) == 0

    _call(app, "GET", "/minihomepy/yuna", query="viewer=stranger")
    assert homepy.visitor_counts["yuna"] == 1


def test_guestbook_post_redirects_and_persists():
    app, _, guestbook, _ = _seeded_app()
    body = urlencode({"author": "새친구", "content": "방가방가", "viewer": "stranger"})
    status, headers, _ = _call(app, "POST", "/minihomepy/yuna/guestbook", body=body)
    assert status == "303 See Other"
    assert headers["Location"] == "/minihomepy/yuna?viewer=stranger"

    _, _, page = _call(app, "GET", "/minihomepy/yuna", query="viewer=stranger")
    assert "새친구" in page and "방가방가" in page


def test_guestbook_post_secret_is_masked_for_others():
    app, _, _, _ = _seeded_app()
    body = urlencode({"author": "몰래", "content": "비밀입니다", "secret": "1", "viewer": "u9"})
    _call(app, "POST", "/minihomepy/yuna/guestbook", body=body)

    _, _, as_stranger = _call(app, "GET", "/minihomepy/yuna", query="viewer=u9")
    assert "비밀입니다" not in as_stranger

    _, _, as_owner = _call(app, "GET", "/minihomepy/yuna", query="viewer=yuna")
    assert "비밀입니다" in as_owner


def test_guestbook_post_with_invalid_utf8_bytes_does_not_500():
    """실제 curl 테스트 중 발견: 손상된 인코딩의 POST 바디가 서버를 500으로 죽였다."""
    app, _, _, _ = _seeded_app()
    malformed_body = b"author=bad\xffname&content=hello&viewer=u9"
    status, _, _ = _call(app, "POST", "/minihomepy/yuna/guestbook", body=malformed_body)
    assert status == "303 See Other"


def test_index_lists_messenger_links():
    app, _, _, _ = _seeded_app()
    _, _, body = _call(app, "GET", "/")
    assert "/messenger/yuna" in body


def test_messenger_list_shows_buddy_and_pending_request():
    app, _, _, _ = _seeded_app()
    status, _, body = _call(app, "GET", "/messenger/yuna")
    assert status == "200 OK"
    assert "minsu" in body  # 시드된 버디
    assert "stranger" in body  # 시드된 대기 요청 발신자


def test_messenger_request_accept_creates_mutual_buddy():
    app, _, _, buddy = _seeded_app()
    _call(app, "POST", "/messenger/minsu/request", body=urlencode({"target": "newbie"}))
    status, headers, _ = _call(
        app, "POST", "/messenger/newbie/accept", body=urlencode({"from": "minsu"}))
    assert status == "303 See Other"
    assert headers["Location"] == "/messenger/newbie"
    assert buddy.is_buddy("minsu", "newbie")
    assert buddy.is_buddy("newbie", "minsu")


def test_messenger_reject_discards_request():
    app, _, _, buddy = _seeded_app()
    _call(app, "POST", "/messenger/minsu/request", body=urlencode({"target": "shy"}))
    _call(app, "POST", "/messenger/shy/reject", body=urlencode({"from": "minsu"}))
    assert not buddy.is_buddy("minsu", "shy")
    assert buddy.pending_requests_for("shy") == []


def test_messenger_presence_update():
    app, _, _, buddy = _seeded_app()
    _call(app, "POST", "/messenger/yuna/presence", body=urlencode({"status": "away"}))
    assert buddy.get_presence("yuna", "yuna") == "away"


def test_messenger_chat_page_renders_conversation_and_marks_read():
    app, _, _, buddy = _seeded_app()
    assert buddy.unread_count("yuna", "minsu") > 0  # 시드 메시지로 안읽음 존재

    status, _, body = _call(app, "GET", "/messenger/yuna/minsu")
    assert status == "200 OK"
    assert "버디버디 접속함" in body
    assert buddy.unread_count("yuna", "minsu") == 0  # 열람으로 읽음 처리


def test_messenger_send_requires_buddy_and_persists_between_two_windows():
    app, _, _, buddy = _seeded_app()

    status, headers, _ = _call(
        app, "POST", "/messenger/yuna/minsu/send", body=urlencode({"content": "안녕 민수야"}))
    assert status == "303 See Other"
    assert headers["Location"] == "/messenger/yuna/minsu"

    # minsu 창(반대편 사용자)에서 대화를 열면 방금 보낸 메시지가 그대로 보인다
    _, _, minsu_view = _call(app, "GET", "/messenger/minsu/yuna")
    assert "안녕 민수야" in minsu_view

    # 버디가 아닌 사이에서는 전송이 무시된다
    _call(app, "POST", "/messenger/yuna/stranger/send", body=urlencode({"content": "몰래"}))
    assert buddy.get_conversation("yuna", "stranger") == []


def test_messenger_messages_json_polling_returns_only_new_messages():
    app, _, _, buddy = _seeded_app()
    _, _, body = _call(app, "GET", "/messenger/minsu/yuna", query="viewer=minsu")
    last_id = buddy.get_conversation("minsu", "yuna")[-1].id
    del body

    _call(app, "POST", "/messenger/yuna/minsu/send", body=urlencode({"content": "새 메시지"}))
    status, headers, poll_body = _call(
        app, "GET", "/messenger/minsu/yuna/messages.json", query=f"since={last_id}")
    assert status == "200 OK"
    assert headers["Content-Type"].startswith("application/json")
    data = json.loads(poll_body)
    assert [m["content"] for m in data] == ["새 메시지"]

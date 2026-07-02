# -*- coding: utf-8 -*-
"""미니홈피 WSGI 앱: 실제 소켓 없이 WSGI 콜러블을 직접 호출해 라우팅을 검증한다."""
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
    chon, acorn, homepy, guestbook = build_services()
    seed_demo_data(chon, acorn, homepy, guestbook)
    return make_app(chon, acorn, homepy, guestbook), homepy, guestbook


def test_index_lists_seeded_owners():
    app, _, _ = _seeded_app()
    status, _, body = _call(app, "GET", "/")
    assert status == "200 OK"
    assert "/minihomepy/yuna" in body


def test_minihomepy_page_respects_visibility_by_viewer():
    app, _, _ = _seeded_app()

    _, _, as_stranger = _call(app, "GET", "/minihomepy/yuna", query="viewer=stranger")
    assert "안녕하세요" in as_stranger  # 전체공개
    assert "일촌에게만 보이는" not in as_stranger  # 일촌 아님
    assert "비밀 일기" not in as_stranger  # 비공개

    _, _, as_chon = _call(app, "GET", "/minihomepy/yuna", query="viewer=minsu")
    assert "일촌에게만 보이는" in as_chon  # minsu는 yuna와 일촌(시드 데이터)
    assert "비밀 일기" not in as_chon


def test_minihomepy_page_unknown_owner_404():
    app, _, _ = _seeded_app()
    status, _, _ = _call(app, "GET", "/minihomepy/nobody", query="viewer=guest")
    assert status == "404 Not Found"


def test_visit_increments_visitor_count_excluding_self():
    app, homepy, _ = _seeded_app()
    _call(app, "GET", "/minihomepy/yuna", query="viewer=yuna")  # 본인 방문
    assert homepy.visitor_counts.get("yuna", 0) == 0

    _call(app, "GET", "/minihomepy/yuna", query="viewer=stranger")
    assert homepy.visitor_counts["yuna"] == 1


def test_guestbook_post_redirects_and_persists():
    app, _, guestbook = _seeded_app()
    body = urlencode({"author": "새친구", "content": "방가방가", "viewer": "stranger"})
    status, headers, _ = _call(app, "POST", "/minihomepy/yuna/guestbook", body=body)
    assert status == "303 See Other"
    assert headers["Location"] == "/minihomepy/yuna?viewer=stranger"

    _, _, page = _call(app, "GET", "/minihomepy/yuna", query="viewer=stranger")
    assert "새친구" in page and "방가방가" in page


def test_guestbook_post_secret_is_masked_for_others():
    app, _, _ = _seeded_app()
    body = urlencode({"author": "몰래", "content": "비밀입니다", "secret": "1", "viewer": "u9"})
    _call(app, "POST", "/minihomepy/yuna/guestbook", body=body)

    _, _, as_stranger = _call(app, "GET", "/minihomepy/yuna", query="viewer=u9")
    assert "비밀입니다" not in as_stranger

    _, _, as_owner = _call(app, "GET", "/minihomepy/yuna", query="viewer=yuna")
    assert "비밀입니다" in as_owner


def test_guestbook_post_with_invalid_utf8_bytes_does_not_500():
    """실제 curl 테스트 중 발견: 손상된 인코딩의 POST 바디가 서버를 500으로 죽였다."""
    app, _, _ = _seeded_app()
    malformed_body = b"author=bad\xffname&content=hello&viewer=u9"
    status, _, _ = _call(app, "POST", "/minihomepy/yuna/guestbook", body=malformed_body)
    assert status == "303 See Other"

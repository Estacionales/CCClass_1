# -*- coding: utf-8 -*-
"""미니홈피 간단 웹서버: 표준 라이브러리 WSGI만 사용(외부 프레임워크 의존 없음).

실행: python3 -m server.web.app  →  http://127.0.0.1:8000/
"""
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from server.contexts.acorn.service import AcornService
from server.contexts.chon.service import ChonService
from server.contexts.guestbook.service import GuestbookService
from server.contexts.minihomepy import screens
from server.contexts.minihomepy.service import MinihomepyService

DEFAULT_VIEWER = "guest"


def build_services():
    chon = ChonService()
    acorn = AcornService()
    homepy = MinihomepyService(chon=chon, acorn=acorn)
    guestbook = GuestbookService()
    return chon, acorn, homepy, guestbook


def seed_demo_data(chon, acorn, homepy, guestbook):
    """데모용 시드 데이터: 일촌 관계 하나, 다이어리 3종 공개범위, 적용 아이템, 방명록 2건."""
    for user in ("yuna", "minsu"):
        homepy.create_for_user(user)

    homepy.set_profile(
        "yuna", nickname="유나", mood="감성",
        status_message="나는 가끔...\n눈물을 흘린다...\n뉴니거 보에버...☆")
    homepy.set_profile("minsu", nickname="민수", mood="즐거움", status_message="오늘도 출첵!")

    chon.request("minsu", "yuna")
    chon.accept("minsu", "yuna")

    homepy.write_diary("yuna", "yuna", "안녕하세요! 반가워요 :)", "public")
    homepy.write_diary("yuna", "yuna", "일촌에게만 보이는 오늘의 근황", "chon")
    homepy.write_diary("yuna", "yuna", "아무도 못 보는 비밀 일기", "private")

    acorn.charge("yuna", 100, order_id="seed-charge-1")
    acorn.purchase("yuna", "skin-pink", 100, order_id="seed-purchase-1")
    homepy.apply_item("yuna", "skin-pink")

    m1 = guestbook.post("yuna", "minsu", "타운 놀러왔어요! 스킨 예쁘다 ㅎㅎ")
    guestbook.reply(m1, "yuna", "고마워 자주 놀러와~")
    guestbook.post("yuna", "stranger", "너한테만 하는 비밀 얘기", secret=True)


def render_minihomepy(homepy, guestbook, owner, viewer):
    homepy.visit(owner, viewer)
    diary_entries = homepy.list_diary(owner, viewer)
    guestbook_entries = [
        {"author": r.author, "content": r.content, "masked": r.masked, "reply": r.reply}
        for r in (guestbook.read(mid, viewer) for mid in guestbook.list_messages(owner))
    ]
    profile = homepy.get_profile(owner)
    return screens.render_page(
        owner=owner, viewer=viewer,
        nickname=profile["nickname"], mood=profile["mood"],
        status_message=profile["status_message"],
        applied_item=homepy.applied_items.get(owner),
        today_visits=homepy.visits_today(owner),
        total_visits=homepy.visitor_counts.get(owner, 0),
        diary_count=homepy.diary_count(owner),
        guestbook_count=guestbook.count(owner),
        diary_entries=diary_entries,
        guestbook_entries=guestbook_entries,
    )


def render_index(homepy):
    links = "".join(
        f'<li><a href="/minihomepy/{owner}?viewer={DEFAULT_VIEWER}">{owner}</a></li>'
        for owner in sorted(homepy.homepages)
    )
    return (
        "<!DOCTYPE html><html lang=\"ko\"><head><meta charset=\"utf-8\"/>"
        "<title>싸이월드 데모</title></head><body>"
        f"<h1>미니홈피 목록</h1><ul>{links}</ul>"
        "</body></html>"
    )


def _read_body(environ):
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0
    body = environ["wsgi.input"].read(length) if length else b""
    return parse_qs(body.decode("utf-8", errors="replace"))


def make_app(chon, acorn, homepy, guestbook):
    def app(environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET")
        path = environ.get("PATH_INFO", "/")
        query = parse_qs(environ.get("QUERY_STRING", ""))
        parts = [p for p in path.split("/") if p != ""]

        if path == "/":
            start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
            return [render_index(homepy).encode("utf-8")]

        if len(parts) == 2 and parts[0] == "minihomepy" and method == "GET":
            owner = parts[1]
            if owner not in homepy.homepages:
                start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
                return [b"no such minihomepy"]
            viewer = query.get("viewer", [DEFAULT_VIEWER])[0]
            html_bytes = render_minihomepy(homepy, guestbook, owner, viewer).encode("utf-8")
            start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
            return [html_bytes]

        if len(parts) == 3 and parts[0] == "minihomepy" and parts[2] == "guestbook" and method == "POST":
            owner = parts[1]
            form = _read_body(environ)
            author = form.get("author", [""])[0].strip() or "익명"
            content = form.get("content", [""])[0].strip()
            secret = bool(form.get("secret"))
            viewer = form.get("viewer", [DEFAULT_VIEWER])[0]
            if content:
                guestbook.post(owner, author, content, secret=secret)
            start_response("303 See Other",
                            [("Location", f"/minihomepy/{owner}?viewer={viewer}")])
            return [b""]

        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"not found"]

    return app


def main():
    chon, acorn, homepy, guestbook = build_services()
    seed_demo_data(chon, acorn, homepy, guestbook)
    app = make_app(chon, acorn, homepy, guestbook)
    with make_server("127.0.0.1", 8000, app) as server:
        print("싸이월드 데모 서버: http://127.0.0.1:8000/")
        server.serve_forever()


if __name__ == "__main__":
    main()

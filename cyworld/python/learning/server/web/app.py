# -*- coding: utf-8 -*-
"""미니홈피 간단 웹서버: 표준 라이브러리 WSGI만 사용(외부 프레임워크 의존 없음).

실행: python3 -m server.web.app  →  http://127.0.0.1:8000/
"""
import json
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from server.contexts.acorn.service import AcornService
from server.contexts.buddy import screens as buddy_screens
from server.contexts.buddy.service import BuddyService
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
    buddy = BuddyService()
    return chon, acorn, homepy, guestbook, buddy


def seed_demo_data(chon, acorn, homepy, guestbook, buddy):
    """데모용 시드 데이터: 일촌 관계 하나, 다이어리 3종 공개범위, 적용 아이템, 방명록 2건,
    버디버디 버디 관계·대기 요청·시드 메시지."""
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

    buddy.set_presence("yuna", "online")
    buddy.set_presence("minsu", "away")
    buddy.request("minsu", "yuna")
    buddy.accept("minsu", "yuna")
    buddy.send_message("minsu", "yuna", "유나야 뭐해~ 나 버디버디 접속함 ㅎㅎ")
    buddy.send_message("yuna", "minsu", "오 나도 접속중! 반가워 :)")
    buddy.request("stranger", "yuna")  # 아직 수락 전 대기 요청 데모


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
    owners = sorted(homepy.homepages)
    homepy_links = "".join(
        f'<li><a href="/minihomepy/{owner}?viewer={DEFAULT_VIEWER}">{owner}</a></li>'
        for owner in owners
    )
    messenger_links = "".join(
        f'<li><a href="/messenger/{owner}">{owner} 메신저</a></li>'
        for owner in owners
    )
    return (
        "<!DOCTYPE html><html lang=\"ko\"><head><meta charset=\"utf-8\"/>"
        "<title>싸이월드 데모</title></head><body>"
        f"<h1>미니홈피 목록</h1><ul>{homepy_links}</ul>"
        f"<h1>버디버디 메신저</h1><ul>{messenger_links}</ul>"
        "</body></html>"
    )


def render_messenger_list(buddy, user):
    my_presence = buddy.get_presence(user, user)
    pending = buddy.pending_requests_for(user)
    buddies = [
        {"name": name, "presence": buddy.get_presence(name, user),
         "unread": buddy.unread_count(user, name)}
        for name in buddy.buddies_of(user)
    ]
    return buddy_screens.render_buddy_list(
        user=user, my_presence=my_presence, pending_senders=pending, buddies=buddies)


def render_messenger_chat(buddy, owner, buddy_name):
    buddy.mark_read(owner, buddy_name)
    msgs = buddy.get_conversation(owner, buddy_name)
    last_id = msgs[-1].id if msgs else 0
    messages = [{"sender": m.sender, "content": m.content, "ts": m.ts} for m in msgs]
    presence = buddy.get_presence(buddy_name, owner)
    return buddy_screens.render_chat(owner=owner, buddy=buddy_name, buddy_presence=presence,
                                      messages=messages, last_id=last_id)


def _read_body(environ):
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0
    body = environ["wsgi.input"].read(length) if length else b""
    return parse_qs(body.decode("utf-8", errors="replace"))


MESSENGER_ACTIONS = {"request", "accept", "reject", "presence"}


def make_app(chon, acorn, homepy, guestbook, buddy):
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

        if len(parts) == 2 and parts[0] == "messenger" and method == "GET":
            user = parts[1]
            html_bytes = render_messenger_list(buddy, user).encode("utf-8")
            start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
            return [html_bytes]

        if (len(parts) == 3 and parts[0] == "messenger" and parts[2] in MESSENGER_ACTIONS
                and method == "POST"):
            user, action = parts[1], parts[2]
            form = _read_body(environ)
            if action == "request":
                target = form.get("target", [""])[0].strip()
                if target:
                    buddy.request(user, target)
            elif action == "accept":
                from_user = form.get("from", [""])[0].strip()
                if from_user:
                    buddy.accept(from_user, user)
            elif action == "reject":
                from_user = form.get("from", [""])[0].strip()
                if from_user:
                    buddy.reject(from_user, user)
            elif action == "presence":
                status = form.get("status", [""])[0].strip()
                if status in ("online", "away", "offline"):
                    buddy.set_presence(user, status)
            start_response("303 See Other", [("Location", f"/messenger/{user}")])
            return [b""]

        if (len(parts) == 3 and parts[0] == "messenger" and parts[2] not in MESSENGER_ACTIONS
                and method == "GET"):
            user, buddy_name = parts[1], parts[2]
            html_bytes = render_messenger_chat(buddy, user, buddy_name).encode("utf-8")
            start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
            return [html_bytes]

        if len(parts) == 4 and parts[0] == "messenger" and parts[3] == "send" and method == "POST":
            user, buddy_name = parts[1], parts[2]
            form = _read_body(environ)
            content = form.get("content", [""])[0].strip()
            if content:
                buddy.send_message(user, buddy_name, content)
            start_response("303 See Other",
                            [("Location", f"/messenger/{user}/{buddy_name}")])
            return [b""]

        if (len(parts) == 4 and parts[0] == "messenger" and parts[3] == "messages.json"
                and method == "GET"):
            user, buddy_name = parts[1], parts[2]
            try:
                since_id = int(query.get("since", ["0"])[0])
            except ValueError:
                since_id = 0
            buddy.mark_read(user, buddy_name)
            msgs = buddy.get_conversation(user, buddy_name, since_id=since_id)
            payload = [{"id": m.id, "sender": m.sender, "content": m.content, "ts": m.ts}
                       for m in msgs]
            start_response("200 OK", [("Content-Type", "application/json; charset=utf-8")])
            return [json.dumps(payload).encode("utf-8")]

        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"not found"]

    return app


def main():
    chon, acorn, homepy, guestbook, buddy = build_services()
    seed_demo_data(chon, acorn, homepy, guestbook, buddy)
    app = make_app(chon, acorn, homepy, guestbook, buddy)
    with make_server("127.0.0.1", 8000, app) as server:
        print("싸이월드 데모 서버: http://127.0.0.1:8000/")
        server.serve_forever()


if __name__ == "__main__":
    main()

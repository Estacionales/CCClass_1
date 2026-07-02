# -*- coding: utf-8 -*-
"""버디버디 메신저 화면 렌더: 순수 함수(서비스 상태를 직접 만지지 않는다).

참조 이미지가 없어(`sdd/00_sources`에 버디버디 목업 미보유) 요구사항에서 직접 도출한
원 인터페이스(버디 리스트 + 1:1 채팅창)로 새로 설계했다 — 실 버디버디 서비스의
UI 자산·상표는 재현하지 않는다. 경계는 `sdd/01_planning/02_screen/buddy_screen_spec.md`
참고.

호출자(server/web/app.py)가 서비스에서 뷰모델을 뽑아 넘기면 HTML을 생성한다.
사용자 입력은 모두 html.escape로 이스케이프한다(XSS 방지). 채팅 폴링 스크립트는
추가로 클라이언트에서 `textContent`만 사용해 DOM에 삽입한다(서버 렌더가 실수로
이스케이프를 빠뜨려도 HTML로 해석되지 않도록 하는 이중 방어).
"""
import json
from html import escape

PRESENCE_DOT = {"online": ("●", "#2f9e44"), "away": ("●", "#f08c00"),
                "offline": ("○", "#adb5bd"), "unknown": ("○", "#adb5bd")}
PRESENCE_LABEL = {"online": "온라인", "away": "자리비움", "offline": "오프라인",
                  "unknown": "알수없음"}

PAGE_STYLE = """
* { box-sizing: border-box; }
body {
  font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
  margin: 0; padding: 2rem; color: #222; background: #fff6e0;
}
.messenger-frame {
  max-width: 460px; margin: 0 auto; background: #fff;
  border: 4px solid #ffb703; border-radius: 16px; overflow: hidden;
  box-shadow: 0 6px 18px rgba(0,0,0,.15);
}
.messenger-header {
  background: #ffb703; color: #4a2e00; padding: .8rem 1rem;
  display: flex; align-items: center; justify-content: space-between;
}
.messenger-header h1 { font-size: 1.05rem; margin: 0; }
.presence-form select { padding: .2rem; border-radius: 6px; border: none; }
.card { padding: .9rem 1rem; border-bottom: 1px solid #f1e3c6; }
.card:last-child { border-bottom: none; }
h2.section-title { font-size: .9rem; color: #a9720c; margin: 0 0 .5rem; }
.buddy-row {
  display: flex; align-items: center; gap: .5rem; padding: .4rem 0;
  text-decoration: none; color: #222;
}
.buddy-row .name { flex: 1; }
.unread-badge {
  background: #e8590c; color: #fff; font-size: .72rem; border-radius: 10px;
  padding: .1rem .5rem;
}
.request-row { display: flex; align-items: center; gap: .5rem; padding: .3rem 0; }
.request-row form { display: inline; margin: 0; }
button { padding: .35rem .8rem; border: none; border-radius: 6px;
  background: #ffb703; color: #4a2e00; cursor: pointer; font-weight: bold; }
button.reject { background: #e9ecef; color: #495057; }
input[name="target"], input[name="content"] {
  padding: .4rem; border: 1px solid #f1cf87; border-radius: 6px; width: 70%;
}
.empty { color: #999; font-size: .85rem; }
#chat-log {
  height: 320px; overflow-y: auto; padding: .8rem; background: #fffaf0;
  display: flex; flex-direction: column; gap: .4rem;
}
.msg { max-width: 75%; padding: .4rem .7rem; border-radius: 10px; font-size: .9rem; }
.msg .who { display: block; font-size: .7rem; opacity: .6; margin-bottom: .1rem; }
.msg.mine { align-self: flex-end; background: #ffe066; }
.msg.theirs { align-self: flex-start; background: #eef1f5; }
.chat-input-row { display: flex; gap: .5rem; padding: .8rem 1rem; }
.chat-input-row input { flex: 1; }
"""


def render_presence_dot(status):
    glyph, color = PRESENCE_DOT.get(status, PRESENCE_DOT["unknown"])
    label = PRESENCE_LABEL.get(status, status)
    return f'<span style="color:{color}" title="{escape(label)}">{glyph}</span>'


def render_pending_requests(user, senders):
    if not senders:
        return '<p class="empty">받은 버디 요청이 없습니다.</p>'
    rows = []
    for sender in senders:
        safe_sender = escape(sender)
        rows.append(
            '<div class="request-row">'
            f'<span class="name">{safe_sender}</span>'
            f'<form method="post" action="/messenger/{escape(user)}/accept">'
            f'<input type="hidden" name="from" value="{safe_sender}"/>'
            '<button type="submit">수락</button></form>'
            f'<form method="post" action="/messenger/{escape(user)}/reject">'
            f'<input type="hidden" name="from" value="{safe_sender}"/>'
            '<button type="submit" class="reject">거절</button></form>'
            '</div>'
        )
    return "".join(rows)


def render_buddy_rows(user, buddies):
    """buddies: [{"name": str, "presence": str, "unread": int}]"""
    if not buddies:
        return '<p class="empty">아직 버디가 없습니다. 아래에서 요청해보세요.</p>'
    rows = []
    for b in buddies:
        safe_name = escape(b["name"])
        badge = (f'<span class="unread-badge">{b["unread"]}</span>'
                 if b["unread"] else "")
        rows.append(
            f'<a class="buddy-row" href="/messenger/{escape(user)}/{safe_name}">'
            f'{render_presence_dot(b["presence"])}'
            f'<span class="name">{safe_name}</span>{badge}</a>'
        )
    return "".join(rows)


def render_buddy_list(*, user, my_presence, pending_senders, buddies):
    options = "".join(
        f'<option value="{s}"{" selected" if s == my_presence else ""}>'
        f'{escape(PRESENCE_LABEL[s])}</option>'
        for s in ("online", "away", "offline")
    )
    return (
        "<!DOCTYPE html><html lang=\"ko\"><head>"
        f'<meta charset="utf-8"/><title>{escape(user)}의 버디버디</title>'
        f"<style>{PAGE_STYLE}</style>"
        "</head><body>"
        '<div class="messenger-frame">'
        '<div class="messenger-header">'
        f'<h1>{escape(user)}의 버디 리스트</h1>'
        '<form class="presence-form" method="post" '
        f'action="/messenger/{escape(user)}/presence">'
        f'<select name="status" onchange="this.form.submit()">{options}</select>'
        '</form></div>'
        '<div class="card">'
        '<h2 class="section-title">받은 버디 요청</h2>'
        + render_pending_requests(user, pending_senders) +
        '</div>'
        '<div class="card">'
        '<h2 class="section-title">내 버디</h2>'
        + render_buddy_rows(user, buddies) +
        '</div>'
        '<div class="card">'
        '<h2 class="section-title">버디 추가</h2>'
        f'<form method="post" action="/messenger/{escape(user)}/request">'
        '<input name="target" placeholder="상대 아이디" required/>'
        '<button type="submit">요청 보내기</button>'
        '</form></div>'
        "</div></body></html>"
    )


def render_message(owner, msg):
    cls = "mine" if msg["sender"] == owner else "theirs"
    return (
        f'<div class="msg {cls}">'
        f'<span class="who">{escape(msg["sender"])}</span>'
        f'{escape(msg["content"])}</div>'
    )


def render_chat(*, owner, buddy, buddy_presence, messages, last_id):
    log = "".join(render_message(owner, m) for m in messages) or (
        '<p class="empty">아직 대화가 없습니다. 첫 메시지를 보내보세요!</p>')
    owner_json = json.dumps(owner)
    buddy_json = json.dumps(buddy)
    return (
        "<!DOCTYPE html><html lang=\"ko\"><head>"
        f'<meta charset="utf-8"/><title>{escape(owner)} ↔ {escape(buddy)}</title>'
        f"<style>{PAGE_STYLE}</style>"
        "</head><body>"
        '<div class="messenger-frame">'
        '<div class="messenger-header">'
        f'<h1>{render_presence_dot(buddy_presence)} {escape(buddy)}</h1>'
        f'<a href="/messenger/{escape(owner)}" style="color:#4a2e00">← 목록</a>'
        '</div>'
        f'<div id="chat-log">{log}</div>'
        '<form id="send-form" class="chat-input-row" '
        f'action="/messenger/{escape(owner)}/{escape(buddy)}/send" method="post">'
        '<input id="content-input" name="content" placeholder="메시지 입력..." '
        'autocomplete="off" required/>'
        '<button type="submit">전송</button>'
        '</form>'
        '<script>'
        f'(function(){{var OWNER={owner_json},BUDDY={buddy_json},lastId={last_id};'
        'var log=document.getElementById("chat-log");'
        'function appendMsg(m){'
        'var div=document.createElement("div");'
        'div.className="msg "+(m.sender===OWNER?"mine":"theirs");'
        'var who=document.createElement("span");who.className="who";'
        'who.textContent=m.sender;'
        'div.appendChild(who);'
        'div.appendChild(document.createTextNode(m.content));'
        'log.appendChild(div);lastId=m.id;}'
        'function poll(){'
        'fetch("/messenger/"+encodeURIComponent(OWNER)+"/"+encodeURIComponent(BUDDY)'
        '+"/messages.json?since="+lastId)'
        '.then(function(r){return r.json();})'
        '.then(function(data){data.forEach(appendMsg);log.scrollTop=log.scrollHeight;});}'
        'setInterval(poll,2000);'
        'log.scrollTop=log.scrollHeight;'
        'document.getElementById("send-form").addEventListener("submit",function(ev){'
        'ev.preventDefault();'
        'var input=document.getElementById("content-input");'
        'var content=input.value;if(!content)return;'
        'fetch(this.action,{method:"POST",'
        'headers:{"Content-Type":"application/x-www-form-urlencoded"},'
        'body:"content="+encodeURIComponent(content)})'
        '.then(function(){input.value="";poll();});});'
        '})();'
        '</script>'
        "</div></body></html>"
    )

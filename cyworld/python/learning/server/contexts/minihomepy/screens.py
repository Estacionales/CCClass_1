# -*- coding: utf-8 -*-
"""미니홈피 화면 렌더: 순수 함수(서비스 상태를 직접 만지지 않는다).

`sdd/00_sources/image.png` 참조 목업(하늘색 바인더 프레임 + 그리드 텍스처 배경 +
좌측 프로필 사이드바 + 통계 바 + 우측 탭)을 CSS만으로 재현한다. 실제 픽셀아트
일러스트(미니룸·프로필 사진)는 이 환경에 자산 빌더·이미지 자산이 없어 자리표시자로
대체했다 — `sdd/04_verify/02_screen/minihomepy.md`에 그 경계를 기록한다.

호출자(server/web/app.py)가 서비스에서 뷰모델을 뽑아 넘기면 HTML을 생성한다.
사용자 입력은 모두 html.escape로 이스케이프한다(XSS 방지).
"""
from html import escape

VISIBILITY_LABEL = {"public": "전체공개", "chon": "일촌공개", "private": "비공개"}

PAGE_STYLE = """
* { box-sizing: border-box; }
body {
  font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
  margin: 0; padding: 2rem; color: #333;
  /* 참조 이미지의 회색 그리드 텍스처 배경 */
  background-color: #d8d8d8;
  background-image:
    linear-gradient(#c9c9c9 1px, transparent 1px),
    linear-gradient(90deg, #c9c9c9 1px, transparent 1px);
  background-size: 16px 16px;
}
.frame {
  position: relative; max-width: 820px; margin: 0 auto;
  background: #eaf7fc; border: 10px solid #4fc3e8; border-radius: 22px;
  box-shadow: 0 8px 24px rgba(0,0,0,.25);
}
.frame::before, .frame::after {
  content: ""; position: absolute; top: -26px; width: 22px; height: 22px;
  background: #1b3a57; border-radius: 50%; box-shadow: inset 0 2px 3px rgba(0,0,0,.5);
}
.frame::before { left: 28px; } .frame::after { right: 28px; }
.frame-header {
  display: flex; align-items: baseline; justify-content: space-between;
  padding: 1rem 1.5rem 0.5rem; border-bottom: 2px solid #bfe9f7;
}
.visit-stats { font-size: .8rem; color: #555; }
.visit-stats b.total { color: #e8590c; }
.frame-title { font-size: 1.4rem; color: #2596be; margin: 0; flex: 1; text-align: center; }
.brand { font-size: .75rem; color: #888; }
.frame-body { display: flex; gap: 1rem; padding: 1rem 1.5rem 1.5rem; }
.sidebar { width: 200px; flex-shrink: 0; }
.side-tabs { width: 70px; flex-shrink: 0; display: flex; flex-direction: column; gap: .4rem; }
.side-tabs a {
  display: block; text-align: center; padding: .6rem .3rem; border-radius: 8px 0 0 8px;
  background: #dff3fb; color: #2596be; text-decoration: none; font-size: .85rem;
}
.side-tabs a.active { background: #4fc3e8; color: #fff; font-weight: bold; }
.side-tabs a.disabled { color: #aaa; cursor: default; }
.main-panel { flex: 1; min-width: 0; }
.card {
  background: #fff; border-radius: 10px; padding: .9rem 1rem; margin-bottom: .9rem;
  box-shadow: 0 2px 4px rgba(0,0,0,.08);
}
.profile-photo-box { text-align: center; }
.mood-badge {
  display: inline-block; background: #4fc3e8; color: #fff; font-size: .75rem;
  padding: .25rem .6rem; border-radius: 12px; margin-bottom: .5rem;
}
.photo-placeholder {
  font-size: 3.5rem; background: #f1f1f1; border-radius: 8px; padding: 1.2rem 0;
  margin-bottom: .5rem;
}
.profile-caption { font-size: .85rem; line-height: 1.4; white-space: pre-wrap; }
.profile-links { font-size: .75rem; color: #2596be; margin-top: .4rem; }
.wave-button {
  display: block; text-align: center; margin-top: .6rem; padding: .5rem;
  background: #ff7a3d; color: #fff; border-radius: 8px; font-size: .8rem; font-weight: bold;
}
.stats-row { display: flex; gap: 1.2rem; font-size: .85rem; }
.stats-row b { color: #2596be; }
.music-player { display: flex; align-items: center; gap: .5rem; font-size: .85rem; color: #555; }
h2.section-title { font-size: 1rem; color: #2596be; margin: 0 0 .5rem; }
.entry { margin-bottom: .6rem; font-size: .9rem; }
.entry.reply { margin-left: 1rem; color: #777; font-size: .82rem; }
.badge { font-size: .72rem; color: #888; margin-right: .3rem; }
.secret { color: #aaa; font-style: italic; }
.miniroom-scene {
  font-size: 2.2rem; text-align: center; background: #ffb066;
  border-radius: 8px; padding: 1.4rem 0; letter-spacing: .5rem;
}
input, textarea {
  display: block; margin: .3rem 0; width: 100%; padding: .4rem;
  border: 1px solid #cfe8f2; border-radius: 6px;
}
button { padding: .4rem .9rem; border: none; border-radius: 6px;
  background: #4fc3e8; color: #fff; cursor: pointer; }
"""


def render_stats_bar(today_visits, total_visits):
    return (
        '<div class="visit-stats">'
        f"TODAY {today_visits} | TOTAL <b class=\"total\">{total_visits:,}</b>"
        "</div>"
    )


def render_profile_sidebar(*, owner, nickname, mood, status_message):
    mood_label = escape(mood) if mood else "오늘의 기분"
    caption = escape(status_message) if status_message else "아직 등록된 상태메시지가 없습니다."
    return (
        '<aside class="sidebar">'
        '<div class="card profile-photo-box">'
        f'<div class="mood-badge">TODAY IS... {mood_label}</div>'
        '<div class="photo-placeholder">\U0001F994</div>'
        f'<p class="profile-caption">{caption}</p>'
        '<div class="profile-links">EDIT · HISTORY</div>'
        '</div>'
        f'<a class="wave-button" href="/minihomepy/{escape(owner)}?viewer=guest">'
        f'★ {escape(nickname)} 파도타기</a>'
        '</aside>'
    )


def render_nav_tabs(owner, active="home"):
    tabs = [("home", "홈", f"/minihomepy/{owner}#top"), ("photo", "사진첩", None),
            ("diary", "다이어리", f"/minihomepy/{owner}#diary"),
            ("guestbook", "방명록", f"/minihomepy/{owner}#guestbook")]
    links = []
    for key, label, href in tabs:
        cls = "active" if key == active else ("disabled" if href is None else "")
        target = href or "#"
        links.append(f'<a class="{cls}" href="{escape(target)}">{label}</a>')
    return f'<nav class="side-tabs">{"".join(links)}</nav>'


def render_stats_and_player(diary_count, guestbook_count):
    return (
        '<div class="card">'
        '<div class="stats-row">'
        f"<span>다이어리 <b>{diary_count}</b></span>"
        f"<span>방명록 <b>{guestbook_count}</b></span>"
        "<span>사진첩 <b>0</b></span>"
        "</div>"
        '<div class="music-player" style="margin-top:.6rem">'
        "\U0001F3B5 재생목록 준비중 &nbsp; ⏯ &#9654; &#9197;"
        "</div>"
        "</div>"
    )


def render_friends_say(entries):
    visible = [e for e in entries if not e["masked"]][:2]
    if not visible:
        body = '<p class="entry">아직 친구들의 한마디가 없습니다.</p>'
    else:
        body = "".join(
            f'<div class="entry">{escape(e["author"])} ♡ {escape(e["content"])}</div>'
            for e in visible
        )
    return f'<div class="card"><h2 class="section-title">What Friends say</h2>{body}</div>'


def render_miniroom():
    return (
        '<div class="card">'
        '<h2 class="section-title">Miniroom</h2>'
        '<div class="miniroom-scene">\U0001F994\U0001F3E0\U0001F5A5️</div>'
        "</div>"
    )


def render_diary(entries):
    if not entries:
        items = "<p>작성된 다이어리가 없습니다.</p>"
    else:
        items = "".join(
            '<div class="entry">'
            f'<span class="badge">[{VISIBILITY_LABEL.get(e["visibility"], e["visibility"])}]</span> '
            f'{escape(e["content"])}'
            "</div>"
            for e in entries
        )
    return f'<div id="diary" class="card"><h2 class="section-title">다이어리</h2>{items}</div>'


def render_guestbook(owner, entries, viewer="guest"):
    if not entries:
        rows = "<p>방명록이 비어 있습니다.</p>"
    else:
        rows = "".join(_render_guestbook_entry(e) for e in entries)
    form = (
        f'<form method="post" action="/minihomepy/{escape(owner)}/guestbook">'
        f'<input type="hidden" name="viewer" value="{escape(viewer)}"/>'
        '<input name="author" placeholder="당신의 이름" required/>'
        '<textarea name="content" placeholder="방명록 메시지" required></textarea>'
        '<label><input type="checkbox" name="secret" value="1"/> 비밀글</label>'
        '<button type="submit">남기기</button>'
        "</form>"
    )
    return (
        f'<div id="guestbook" class="card">'
        f'<h2 class="section-title">방명록</h2>{rows}{form}</div>'
    )


def _render_guestbook_entry(entry):
    content_cls = "secret" if entry["masked"] else ""
    author = escape(entry["author"])
    content = escape(entry["content"])
    reply = (
        f'<div class="entry reply">↳ 주인 답글: {escape(entry["reply"])}</div>'
        if entry.get("reply") else ""
    )
    return (
        f'<div class="entry"><b>{author}</b>: '
        f'<span class="{content_cls}">{content}</span></div>{reply}'
    )


def render_page(*, owner, viewer, nickname, mood, status_message, applied_item,
                 today_visits, total_visits, diary_count, guestbook_count,
                 diary_entries, guestbook_entries):
    del applied_item  # 스킨 시각 렌더는 범위 밖(아이템명은 프로필 카드에 노출하지 않음)
    return (
        "<!DOCTYPE html><html lang=\"ko\"><head>"
        f'<meta charset="utf-8"/><title>{escape(owner)}의 미니홈피</title>'
        f"<style>{PAGE_STYLE}</style>"
        "</head><body>"
        '<div class="frame" id="top">'
        '<div class="frame-header">'
        + render_stats_bar(today_visits, total_visits)
        + f'<h1 class="frame-title">{escape(nickname)}의 추억 상자..♡</h1>'
        '<div class="brand">cyworld demo</div>'
        "</div>"
        '<div class="frame-body">'
        + render_profile_sidebar(owner=owner, nickname=nickname, mood=mood,
                                  status_message=status_message)
        + '<main class="main-panel">'
        + render_stats_and_player(diary_count, guestbook_count)
        + render_friends_say(guestbook_entries)
        + render_miniroom()
        + render_diary(diary_entries)
        + render_guestbook(owner, guestbook_entries, viewer)
        + "</main>"
        + render_nav_tabs(owner)
        + "</div></div></body></html>"
    )

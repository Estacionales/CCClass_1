# 미니홈피 화면 · current-state

> 03_build: Overwrite Rule(지금 상태 1벌).

## Absorbed Planning
- `01_planning/02_screen/minihomepy_screen_spec.md` (레퍼런스: `00_sources/image.png`)
- `02_plan/02_screen/minihomepy_screen_todos.md` (T1~T7 전부 완료)

## Runtime Assembly
- `server/contexts/minihomepy/screens.py` : 순수 렌더 함수 모음.
  - `render_page` : 프레임 전체 조립(헤더+사이드바+메인패널+탭)
  - `render_stats_bar` : `TODAY n | TOTAL n,nnn`
  - `render_profile_sidebar` : 무드뱃지·사진 자리표시자·캡션·EDIT/HISTORY·파도타기 버튼
  - `render_stats_and_player` : 다이어리/방명록/사진첩 카운트 + 뮤직 플레이어 자리표시자
  - `render_friends_say` : 마스킹 안 된 방명록 상위 2건
  - `render_miniroom` : 이모지 자리표시자(실 일러스트 없음)
  - `render_diary` / `render_guestbook` : 기존 로직 유지, 카드 스타일로 재포장
  - `render_nav_tabs` : 홈(활성)/사진첩(비활성)/다이어리·방명록(앵커 링크)
  - `PAGE_STYLE` : 바인더 프레임(`::before/::after` 원형 구멍)·그리드 텍스처 배경·카드
    그림자·컬러 팔레트(하늘색 #4fc3e8, 오렌지 #ff7a3d 포인트)를 CSS만으로 재현
- `server/web/app.py` : `render_minihomepy`가 `MinihomepyService.get_profile`·
  `diary_count`·`visits_today`·`GuestbookService.count`를 조회해 뷰모델 조립 후
  `screens.render_page` 호출
- `server/contexts/minihomepy/service.py` (확장) : `set_profile`/`get_profile`(닉네임·
  무드·상태메시지), `diary_count`, `visits_today`(일 단위 방문자수, 기존 누적
  `visitor_counts`는 유지)
- `server/contexts/guestbook/service.py` (확장) : `count(owner)`

## Modules
| 모듈 | 책임 |
| --- | --- |
| `contexts/minihomepy/screens.py` | 레퍼런스 스타일 화면 HTML 렌더(순수 함수) |
| `web/app.py` | WSGI 라우팅·폼 처리·시드 데이터·뷰모델 조립 |
| `contexts/minihomepy/service.py` | 프로필·다이어리 카운트·오늘/전체 방문자수 (신규 3종) |
| `contexts/guestbook/service.py` | 방명록 개수 조회 (신규 1종) |

## Current Behavior
`GET /minihomepy/<owner>?viewer=<viewer>` 요청 시 하늘색 바인더 프레임 안에 상단
TODAY/TOTAL 방문자 통계, 좌측 프로필 사이드바(무드·상태메시지·파도타기 버튼), 우측에
다이어리/방명록/사진첩 개수·뮤직 플레이어 자리표시자·"What Friends say"·"Miniroom"
자리표시자·전체 다이어리·방명록이 카드 형태로 배치되고, 우측 세로 탭(홈/사진첩/다이어리/
방명록)이 있다. 배경은 CSS 그리드 패턴으로 레퍼런스의 텍스처를 재현했다.

## Not Yet Implemented
- 실제 로그인/세션 없음(viewer는 쿼리 파라미터로만 전달 — 데모 목적, 이전 슬라이스와 동일).
- Miniroom 픽셀아트·프로필 사진: 실 이미지 자산 없음(이모지 자리표시자로 대체).
- 뮤직 플레이어 실제 재생 기능, 사진첩 기능 자체: 범위 밖(정적 자리표시자).

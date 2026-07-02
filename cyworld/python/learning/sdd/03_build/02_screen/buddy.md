# 버디버디 메신저 화면 · current-state

> 03_build: Overwrite Rule(지금 상태 1벌).

## Absorbed Planning
- `01_planning/02_screen/buddy_screen_spec.md` (참조 이미지 없음 — 원 인터페이스로 설계)
- `02_plan/02_screen/buddy_screen_todos.md` (T1~T7 전부 완료)

## Runtime Assembly
- `server/contexts/buddy/screens.py` : 순수 렌더 함수 모음.
  - `render_buddy_list` : 상태 셀렉트(즉시 POST) + 받은 요청(수락/거절) + 버디 목록
    (상태점·안읽음 배지) + 새 버디 요청 폼
  - `render_chat` : 말풍선 대화 로그(본인 우측/상대 좌측) + 전송 폼 + 2초 폴링·fetch
    전송 인라인 스크립트(서버가 렌더한 `owner`/`buddy`는 `json.dumps`로 JS 문자열
    이스케이프, 수신 메시지는 `textContent`로만 DOM 삽입)
  - `render_presence_dot` : 온라인(●초록)/자리비움(●주황)/오프라인·알수없음(○회색)
  - `PAGE_STYLE` : 버디버디 원 인터페이스 — 주황(#ffb703) 프레임, 채팅 버블 배색
- `server/web/app.py` (확장) :
  - `render_messenger_list` / `render_messenger_chat` : 서비스 조회 → 뷰모델 조립 →
    `buddy_screens` 호출 (채팅 진입 시 `mark_read` 호출)
  - 라우팅 8종: `GET /messenger/<user>`, `POST /messenger/<user>/{request,accept,reject,
    presence}`, `GET /messenger/<user>/<buddy>`, `POST /messenger/<user>/<buddy>/send`,
    `GET /messenger/<user>/<buddy>/messages.json`
  - `build_services`/`seed_demo_data`/`make_app` 시그니처에 `buddy` 추가(5-튜플)
  - 루트 인덱스에 "버디버디 메신저" 링크 섹션 추가
  - 시드 데이터: yuna(온라인)·minsu(자리비움) 버디 관계 + 시드 메시지 2건,
    stranger→yuna 대기 요청 1건

## Modules
| 모듈 | 책임 |
| --- | --- |
| `contexts/buddy/screens.py` | 버디 리스트·채팅 화면 HTML 렌더(순수 함수) |
| `web/app.py` | 메신저 라우팅·폼 처리·폴링 JSON 엔드포인트·시드 데이터 확장 |
| `contexts/buddy/service.py` | 요청·수락·거절·전송·대화·상태·안읽음 (03_build/01_feature 참고) |

## Current Behavior
`GET /messenger/<user>`는 상태 변경 셀렉트, 받은 버디 요청(수락/거절 버튼), 내 버디 목록
(상태점 + 안읽음 배지), 새 버디 요청 폼을 카드로 보여준다. `GET /messenger/<user>/<buddy>`
는 대화 전체를 말풍선으로 보여주고(본인 메시지는 우측 노란 말풍선, 상대는 좌측 회색),
입력창에서 전송하면 새로고침 없이 즉시 반영되며, 2초마다 `messages.json`을 폴링해 상대가
보낸 새 메시지를 자동으로 append한다. 대화 페이지를 열거나 폴링이 일어나면 상대가 보낸
메시지가 읽음 처리되어 목록 화면의 안읽음 배지가 사라진다.

## Not Yet Implemented
- 실제 로그인/세션 없음(URL 경로의 사용자 세그먼트로 신원 대체 — 기존 미니홈피 데모와
  동일한 제약).
- WebSocket 기반 실시간 전송 없음(2초 폴링으로 대체 — `sdd/01_planning/02_screen/
  buddy_screen_spec.md`의 알려진 경계 참고).
- `request`/`accept`/`reject`/`presence`는 예약어라 실제 사용자 아이디로 쓸 수 없다(데모
  범위에서는 허용 가능한 제약으로 판단, 별도 검증/충돌 처리 없음).

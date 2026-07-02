# 버디버디 메신저 화면 · 검증 (retained)

> proof: `python3 proof/run_proof.py` → 74/74 PASS (exit 0), 그 중 화면 렌더 5건 +
> 웹서버 라우팅 8건(신규) + 기존 웹서버 라우팅 7건(회귀, 시그니처 변경으로 전체 재실행).
> 실행: Python 3.14.6, `tmp/proof-results.json` (2026-07-02).
> 이 환경은 브라우저·Playwright가 없어 렌더 유닛테스트 + 실제 WSGI 서버 기동 후
> curl 스모크 + **실 2인 왕복 시나리오 재현**으로 검증했다(아래 수동 스모크 참고).

## 자동 테스트

| 분면 | 검증 대상 | 결과 |
| --- | --- | --- |
| 렌더 | 버디 리스트(요청/버디/안읽음 배지/선택된 상태) | PASS · `test_render_buddy_list` |
| 렌더 | 버디 리스트 빈 상태(요청 없음/버디 없음) | PASS · `test_render_buddy_list_empty_states` |
| 렌더 | 채팅(본인/상대 말풍선 클래스, 폴링 시작 id) | PASS · `test_render_chat` |
| 렌더 | 채팅 빈 상태 | PASS · `test_render_chat_empty_state` |
| 보안 | 리스트·채팅 전체 입력 HTML 이스케이프(XSS) | PASS · `test_render_escapes_user_content` |
| 라우팅 | 인덱스에 메신저 링크 노출 | PASS · `test_index_lists_messenger_links` |
| 라우팅 | 버디 리스트 페이지(버디/대기요청 표시) | PASS · `test_messenger_list_shows_buddy_and_pending_request` |
| 라우팅 | 요청→수락으로 양방향 버디 생성 | PASS · `test_messenger_request_accept_creates_mutual_buddy` |
| 라우팅 | 거절 시 요청 제거 | PASS · `test_messenger_reject_discards_request` |
| 라우팅 | 상태 변경 반영 | PASS · `test_messenger_presence_update` |
| 라우팅 | 채팅 페이지 렌더 + 열람 시 읽음 처리 | PASS · `test_messenger_chat_page_renders_conversation_and_marks_read` |
| 라우팅 | 전송 후 상대 창에서 동일 메시지 확인, 비버디 전송 무시 | PASS · `test_messenger_send_requires_buddy_and_persists_between_two_windows` |
| 라우팅 | `messages.json` 폴링이 `since` 이후 신규만 반환 | PASS · `test_messenger_messages_json_polling_returns_only_new_messages` |
| 회귀 | 기존 미니홈피/방명록 라우팅 7건(시그니처 변경 후 전량 재실행) | PASS · `test_web_app.py` 기존 케이스 |

## 수동 스모크 (실행 증거 — 실 2인 대화 시나리오)
1. `python3 -m server.web.app` 기동 → `http://127.0.0.1:8000/`.
2. **yuna 창** 역할로 `curl -X POST http://127.0.0.1:8000/messenger/yuna/minsu/send
   --data "content=실시간 테스트 메시지!"` 실행 → `303 See Other` 확인.
3. **minsu 창** 역할로 `curl "http://127.0.0.1:8000/messenger/minsu/yuna/messages.json?since=0"`
   실행 → 방금 보낸 메시지를 포함한 JSON 배열이 즉시 반환됨을 확인(폴링이 실제로
   상대가 보낸 신규 메시지를 가져옴).
4. `curl http://127.0.0.1:8000/messenger/minsu/yuna` 로 채팅 페이지를 열어
   `"실시간 테스트 메시지!"` 문자열이 렌더된 HTML에 포함됨을 확인 → 대화가 대칭적으로
   보임 + 열람 시 안읽음이 0으로 처리됨.
5. 검증 후 서버 프로세스 종료(포트 8000 리스너 PID 확인 후 kill).
6. 브라우저가 있는 환경에서는 curl 대신 실제 두 브라우저 창(또는 시크릿창 2개)을
   `/messenger/yuna/minsu`, `/messenger/minsu/yuna`로 각각 열어 그대로 재현 가능
   (`sdd/01_planning/02_screen/buddy_screen_spec.md`의 2인 로컬 대화 시나리오 참고).

## Residual Risk
- **실 브라우저 렌더링 미검증**: curl 기반 문자열 검증으로 대체했다(기존 미니홈피
  화면 검증과 동일한 제약, 이 환경에 브라우저·Playwright가 없음). 사용자가 직접
  `python3 -m server.web.app` 실행 후 두 브라우저 창으로 열어 확인하는 것을 권장한다.
- **폴링 지연(최대 2초)**: WebSocket이 아니라 표준 라이브러리 제약 내 최소 구현이다.
  실사용에서 메시지가 최대 2초 늦게 보일 수 있다(설계 시 명시한 트레이드오프).
- **UI 자산은 원 인터페이스**: 실 버디버디 서비스의 참조 이미지가 없어 상표·자산을
  재현하지 않고 요구사항에서 직접 설계했다(`buddy_screen_spec.md` 명시).
- 실 로그인/세션 없음(이전 슬라이스들과 동일한 알려진 제약).

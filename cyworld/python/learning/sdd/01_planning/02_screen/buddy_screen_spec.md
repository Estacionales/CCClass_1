# 버디버디 메신저 화면 · 명세

> 소스: 참조 이미지 없음(`sdd/00_sources`에 버디버디 화면 목업 미보유). 이 환경엔
> Asset Spec Builder·디자인 가이드 빌더·Playwright도 없어(`sdd/99_toolchain` 미보유),
> 실 버디버디 서비스의 UI 자산을 재현하지 않고 요구사항(`buddy_feature_spec.md`)에서
> 직접 도출한 **원 인터페이스**(버디 리스트 + 1:1 채팅창)로 새로 설계한다.
> 검증은 실행 가능한 WSGI 서버 + 결정적 HTML 렌더 함수 유닛테스트로 한다(브라우저 비가용).

## 화면 구성

### 1) 버디 리스트 (`GET /messenger/<user>`)
| 영역 | 내용 | 데이터 소스 |
| --- | --- | --- |
| 내 상태 | 온라인/자리비움/오프라인 셀렉트 폼(즉시 POST) | `BuddyService.get_presence(user, user)` |
| 받은 요청 | PENDING 요청 발신자 목록 + 수락/거절 버튼 | `BuddyService.pending_requests_for(user)` |
| 버디 목록 | 버디명 + 상태점(●온라인/●자리비움/○오프라인) + 안읽음 배지 + 대화 링크 | `BuddyService.buddies_of`, `get_presence`, `unread_count` |
| 새 버디 요청 | 상대 아이디 입력 폼(POST) | - |

### 2) 1:1 채팅 (`GET /messenger/<user>/<buddy>`)
| 영역 | 내용 | 데이터 소스 |
| --- | --- | --- |
| 헤더 | 상대 이름 + 상태점 | `get_presence(buddy, user)` |
| 대화 로그 | 메시지 말풍선(본인 우측 정렬, 상대 좌측 정렬), 시간순 | `get_conversation(user, buddy)` |
| 입력창 | 텍스트 입력 + 전송 버튼(폼 POST, fetch로 리로드 없이 전송) | - |
| 실시간성 | 2초 간격 `fetch` 폴링(`/messenger/<user>/<buddy>/messages.json?since=<id>`)으로
  새 메시지만 append. 페이지 재열람·전송 시 `BuddyService.mark_read`가 호출되어
  안읽음이 0이 된다. | - |

## 라우트
- `GET /messenger/<user>` : 버디 리스트 렌더
- `POST /messenger/<user>/request` (`target`) : 버디 요청
- `POST /messenger/<user>/accept` (`from`) : 요청 수락
- `POST /messenger/<user>/reject` (`from`) : 요청 거절
- `POST /messenger/<user>/presence` (`status`) : 상태 변경
- `GET /messenger/<user>/<buddy>` : 대화 페이지(진입 시 `mark_read` 호출)
- `POST /messenger/<user>/<buddy>/send` (`content`) : 메시지 전송(버디 아니면 무시하고
  동일 페이지로 리다이렉트)
- `GET /messenger/<user>/<buddy>/messages.json?since=<id>` : `since` 이후 신규 메시지
  JSON 배열(폴링용, 조회 시 `mark_read`도 함께 호출)

## 2인 로컬 대화 시나리오 (operate 단계에서 실사용)
1. `python3 -m server.web.app` 실행.
2. 브라우저 창 A: `http://127.0.0.1:8000/messenger/yuna/minsu` (yuna로 접속).
3. 브라우저 창 B: `http://127.0.0.1:8000/messenger/minsu/yuna` (minsu로 접속).
4. 양쪽에서 입력창에 메시지를 보내면, 최대 2초 이내에 상대 창에 새로고침 없이 나타난다.

## 보안 고려
- 사용자 이름·메시지 본문은 서버 렌더 시 `html.escape`로 이스케이프한다(XSS 방지).
- 클라이언트 폴링 스크립트는 `textContent`로만 DOM에 삽입해 이중 방어한다(서버 렌더가
  실수로 이스케이프를 빠뜨려도 클라이언트에서 HTML로 해석되지 않는다).
- `owner`/`buddy` 값은 JS 문자열 리터럴로 삽입할 때 `json.dumps`로 인코딩해 따옴표
  주입을 방지한다.

## 알려진 경계 (정직하게 기록)
- 실 로그인/세션 없음(URL 경로 세그먼트로 신원 대체, 기존 미니홈피 데모와 동일한 제약).
- 실시간 전송은 WebSocket이 아닌 짧은 폴링(2초 간격)이다 — 표준 라이브러리
  `wsgiref`만 사용하는 이 환경에서 별도 의존성 없이 "대화 가능"을 만족시키는 선택.
- 실 버디버디 서비스의 마스코트·색상 등 상표 자산은 재현하지 않는다(원 인터페이스).

## 검증 매핑
| 항목 | 테스트 |
| --- | --- |
| 버디 리스트 렌더(상태점·안읽음 배지·요청 목록) | `tests/test_buddy_screen.py::test_render_buddy_list` |
| 대화 렌더(말풍선 정렬·시간순) | `tests/test_buddy_screen.py::test_render_chat` |
| XSS 이스케이프 | `tests/test_buddy_screen.py::test_render_escapes_user_content` |
| 웹서버 라우팅(요청/수락/거절/상태/전송/폴링) | `tests/test_web_app.py::test_messenger_*` |
| 실행 가능한 웹서버 | 수동 스모크: `python3 -m server.web.app` 기동 후 두 브라우저 창으로
  실제 2인 대화 확인(`sdd/04_verify/02_screen/buddy.md`, `sdd/05_operate` 기록) |

# 버디버디 메신저 화면 · todos + 실행 계획

## Scope
버디 리스트 화면 + 1:1 채팅 화면(HTML 렌더 + WSGI 라우팅) 구현, 로컬에서 두 브라우저
창으로 2인이 실제로 대화를 주고받을 수 있는 수준까지 완성.

## Assumptions
- `sdd/99_toolchain`(Asset Spec Builder·디자인 가이드 빌더·Playwright) 미보유 — 참조
  이미지도 없어 요구사항에서 직접 도출한 원 인터페이스로 설계(`buddy_screen_spec.md` 명시).
- 브라우저·Playwright 비가용 환경 — 렌더 함수 유닛테스트 + 실행 가능한 웹서버 curl/수동
  스모크로 검증(기존 미니홈피 화면과 동일한 검증 대체 전략).
- 실시간성은 WebSocket 대신 2초 간격 폴링(표준 라이브러리만 사용하는 제약 내 최소 구현).

## Acceptance Criteria
- `sdd/01_planning/02_screen/buddy_screen_spec.md`의 라우트·렌더 항목 전부 구현.
- 렌더 유닛테스트 + 웹서버 라우팅 테스트 전부 PASS.
- 수동 스모크: 서버 기동 후 두 창(`/messenger/yuna/minsu`, `/messenger/minsu/yuna`)에서
  실제 메시지 왕복 확인.

## Execution Checklist (비중첩)
- [x] T1 @backend-dev  `server/contexts/buddy/screens.py` 버디 리스트 렌더
- [x] T2 @backend-dev  `server/contexts/buddy/screens.py` 채팅 렌더(말풍선·폴링 스크립트)
- [x] T3 @backend-dev  `server/web/app.py` 라우팅 8종(리스트/요청/수락/거절/상태/대화/전송/폴링)
- [x] T4 @backend-dev  시드 데이터 확장(버디 관계·대기 요청·시드 메시지 2건)
- [x] T5 @backend-dev  루트 인덱스 페이지에 메신저 링크 추가
- [x] T6 @test-dev     `tests/test_buddy_screen.py`, `tests/test_web_app.py` 신규 케이스
- [x] T7 @test-dev     수동 스모크(서버 기동 + curl/브라우저) 및 결과 기록

## Regression Scope
- direct: 버디 리스트/채팅 렌더, `/messenger/*` 라우팅
- shared: 웹서버 전체 조립(`build_services`/`seed_demo_data`/`make_app` 시그니처 변경) →
  기존 미니홈피/방명록 라우팅에 회귀 영향 가능성 있어 `test_web_app.py` 기존 케이스 전체
  재실행 필요
- 근거: `sdd/02_plan/10_test/regression_verification.md`

## Current Notes
- 2026-07-02 @backend-dev 요청. `build_services`/`seed_demo_data`/`make_app`이 buddy
  서비스를 추가로 반환·인자로 받도록 시그니처가 바뀌어 기존 웹서버 테스트 전체를 함께
  재검증했다(회귀 없음).

## Validation
- `python3 proof/run_proof.py` 전체 PASS(exit 0) — 기존 51건 + 버디버디 신규 케이스
  전부 포함(`sdd/04_verify/02_screen/buddy.md`, `tmp/proof-results.json`, 2026-07-02).
- 수동 스모크 결과: `sdd/04_verify/02_screen/buddy.md`, 배포 상태: `sdd/05_operate`.

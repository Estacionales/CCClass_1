# 버디버디 메신저(BUDDY) · todos + 실행 계획

## Scope
버디 요청·수락·거절·멱등 재요청, 비버디 전송 거부, 버디 간 1:1 채팅(시간순·대칭 조회),
온라인/자리비움/오프라인 상태(버디에게만 공개), 안읽음 큐잉 + 읽음 처리까지 구현·검증.

## Assumptions
- 실 로그인/세션 없음(기존 도메인과 동일한 데모 제약, 사용자 식별자를 URL/함수 인자로 전달).
- 별도 DEV/PROD 인프라 없음 — 이 저장소는 로컬 단일 프로세스 데모이므로 스테이지드
  롤아웃(DEV→PROD) 게이트는 적용 대상이 아니다. 완료 기준은 로컬 실행 검증 + proof 게이트.
- 영속 저장소(DB) 없음 — 인메모리 서비스(기존 CHON/GUESTBOOK과 동일 패턴), 스키마 정합성
  점검 대상 아님.

## Acceptance Criteria
- AC-1~AC-8 (`sdd/01_planning/01_feature/buddy_feature_spec.md`) 전부 테스트 통과.
- proof 게이트 exit 0 = 완료.

## Execution Checklist (비중첩)
- [x] T1 @backend-dev  버디 요청(PENDING) 생성 (`server/contexts/buddy/service.py`)
- [x] T2 @backend-dev  수락 → 양방향 관계 생성 + 요청 제거
- [x] T3 @backend-dev  재요청 멱등(이미 버디·이미 PENDING)
- [x] T4 @backend-dev  거절 → 요청 제거, 재요청 허용
- [x] T5 @backend-dev  비버디 전송 거부
- [x] T6 @backend-dev  버디 간 메시지 시간순 저장 + 양쪽 대칭 조회
- [x] T7 @backend-dev  상태(온라인/자리비움/오프라인) 설정·버디 전용 공개
- [x] T8 @backend-dev  안읽음 큐잉 + 대화 열람 시 읽음 처리
- [x] T9 @test-dev     proof 게이트 (`tests/test_buddy.py`) — AC-1~AC-8 전부 커버

## Regression Scope
- direct: 버디 요청·수락·거절·메시지 전송·상태·안읽음
- shared: 없음(사용자 존재 여부 확인만 필요, CHON/ACORN/HOMEPY와 직접 의존 없음)
- 근거: `sdd/02_plan/10_test/regression_verification.md`

## Current Notes
- 2026-07-02 @backend-dev 요청으로 AC-1~AC-8 전부 구현. CHON과 달리 TTL·정원은 두지
  않음(요구사항에 없음) — 대신 상태·안읽음이라는 메신저 고유 기능에 집중.
- 화면(웹 UI, 2인 로컬 대화)은 `sdd/02_plan/02_screen/buddy_screen_todos.md`에서 별도 추적.

## Validation
- `python3 proof/run_proof.py` 전체 PASS(exit 0), `tests/test_buddy.py` 포함
  (`sdd/04_verify/01_feature/buddy.md`, `tmp/proof-results.json`, 2026-07-02).

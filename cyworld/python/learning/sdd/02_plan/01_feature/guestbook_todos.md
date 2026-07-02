# 방명록(GUESTBOOK) · todos + 실행 계획

## Scope
방명록 작성·조회, 삭제 권한, 비밀글 마스킹, 주인 답글 제한까지 구현·검증.

## Acceptance Criteria
- AC-1~AC-6 (`sdd/01_planning/01_feature/guestbook_feature_spec.md`) 전부 테스트 통과.
- proof 게이트 exit 0 = 완료.

## Execution Checklist (비중첩)
- [x] T1 @backend-dev  방명록 작성/조회(시간순) (`server/contexts/guestbook/service.py`)
- [x] T2 @backend-dev  삭제 권한(주인·작성자) 검증
- [x] T3 @backend-dev  비밀글 마스킹
- [x] T4 @backend-dev  주인 답글 1개 제한
- [x] T5 @test-dev     proof 게이트 (`tests/test_guestbook.py`) — AC-1~AC-6 전부 커버

## Regression Scope
- direct: 방명록 작성·삭제·답글
- shared: 없음(사용자 존재 여부 확인만 필요)
- 근거: `sdd/02_plan/10_test/regression_verification.md`

## Current Notes
- 2026-07-02 @backend-dev 요청으로 AC-1~AC-6 전부 구현. 외부 컨텍스트 의존 없이 독립 구현.

## Validation
- `python3 proof/run_proof.py` → 22/22 PASS (exit 0), `tests/test_guestbook.py` 4건 포함
  (`sdd/04_verify/01_feature/guestbook.md`, `tmp/proof-results.json`, 2026-07-02).

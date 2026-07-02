# 일촌(CHON) · todos + 실행 계획

## Scope
일촌 요청·수락·거절·만료·정원(750)·파일촌·일촌평까지 구현·검증.

## Acceptance Criteria
- AC-1~AC-7 (`sdd/01_planning/01_feature/chon_feature_spec.md`) 전부 테스트 통과.
- 회귀(미니홈피 일촌공개 접근제어) green. proof 게이트 exit 0 = 완료.

## Execution Checklist (비중첩)
- [x] T1 @backend-dev  일촌 신청(request)/수락(accept) + 재신청 멱등 (`server/contexts/chon/service.py`)
- [x] T2 @backend-dev  TTL(24h) 만료 처리
- [x] T3 @backend-dev  정원(750) 검증 + 파일촌(양방향 제거)
- [x] T4 @backend-dev  일촌평 작성 API(일촌 관계 검증)
- [x] T5 @test-dev     proof 게이트 (`tests/test_chon.py`) — AC-1~AC-7 전부 커버

## Regression Scope
- direct: 일촌 요청·수락·해제·일촌평
- shared: 미니홈피 다이어리 일촌공개 접근제어(`server/contexts/minihomepy`)
- 근거: `sdd/02_plan/10_test/regression_verification.md`

## Current Notes
- 2026-07-02 @backend-dev 요청으로 신청→수락 슬라이스(AC-1~AC-3) 구현.
- 2026-07-02 @backend-dev 요청으로 나머지(TTL·정원·파일촌·일촌평, AC-4~AC-7)까지 구현
  완료. `ChonService`에 `clock` 주입 지원 추가(TTL 결정적 테스트), `_requests` 값을
  status/issued 딕셔너리로 확장.

## Validation
- `python3 proof/run_proof.py` → 28/28 PASS (exit 0), `tests/test_chon.py` 10건 포함
  (`sdd/04_verify/01_feature/chon.md`, `tmp/proof-results.json`, 2026-07-02).

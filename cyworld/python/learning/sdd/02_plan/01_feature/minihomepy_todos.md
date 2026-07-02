# 미니홈피(HOMEPY) · todos + 실행 계획

## Scope
회원가입 연동 자동 생성, 다이어리 공개범위 접근제어, 방문자수 카운트, 스킨/BGM 적용
검증까지 구현·검증.

## Acceptance Criteria
- AC-1~AC-6 (`sdd/01_planning/01_feature/minihomepy_feature_spec.md`) 전부 테스트 통과.
- CHON·ACORN 의존 표면 포함 회귀 green. proof 게이트 exit 0 = 완료.

## Execution Checklist (비중첩)
- [x] T1 @backend-dev  회원가입 훅으로 미니홈피 자동 생성 (`server/contexts/minihomepy/service.py`)
- [x] T2 @backend-dev  다이어리 CRUD + 공개범위(전체/일촌/비공개) 접근제어
- [x] T3 @backend-dev  방문자수 카운트(24시간 중복방지)
- [x] T4 @backend-dev  스킨/BGM 적용 시 acorn 인벤토리 보유 검증(컨텍스트 간 조회)
- [x] T5 @test-dev     proof 게이트 (`tests/test_minihomepy.py`) — AC-1~AC-6 전부 커버

## Regression Scope
- direct: 다이어리·프로필·방문자수
- shared: chon(`server/contexts/chon`) 일촌 관계 조회, acorn(`server/contexts/acorn`) 인벤토리 조회
- 근거: `sdd/02_plan/10_test/regression_verification.md`

## Current Notes
- 2026-07-02 @backend-dev 요청으로 AC-1~AC-6 전부 구현. `MinihomepyService`가 `ChonService`·
  `AcornService` 인스턴스를 생성자 주입으로 참조(단일 프로세스 데모, 별도 API 계약 없음).

## Validation
- `python3 proof/run_proof.py` → 22/22 PASS (exit 0), `tests/test_minihomepy.py` 6건 포함
  (`sdd/04_verify/01_feature/minihomepy.md`, `tmp/proof-results.json`, 2026-07-02).

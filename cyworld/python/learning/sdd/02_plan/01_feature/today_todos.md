# 투데이(TODAY) · todos + 실행 계획

## Scope
하루 한 번 등록(체크인) + 같은 날짜 재요청 멱등 처리.

## Acceptance Criteria
- AC-1~AC-3 (`sdd/01_planning/01_feature/today_feature_spec.md`) 전부 테스트 통과.

## Execution Checklist (비중첩)
- [x] T1 @backend-dev  하루 1회 등록 + 날짜 기준 멱등 (`server/contexts/today/service.py`)
- [x] T2 @test-dev     proof 게이트 (`tests/test_today.py`)

## Regression Scope
- direct: 투데이 등록
- shared: 없음(독립 도메인)

## Current Notes
- 2026-07-02 @backend-dev 요청으로 구현. 날짜는 호출자가 주입(실시간 비의존, 결정적 테스트).

## Validation
- `python3 proof/run_proof.py` → 12/12 PASS (exit 0), `tests/test_today.py` 3건 포함
  (`sdd/04_verify/01_feature/today.md`, `tmp/proof-results.json`, 2026-07-02).

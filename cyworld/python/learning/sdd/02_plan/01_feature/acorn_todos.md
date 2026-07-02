# 도토리(ACORN) · todos + 실행 계획

## Scope
충전(멱등)·구매(인벤토리 반영)·선물(양도)·거래내역(ledger)까지 구현·검증.

## Acceptance Criteria
- AC-1~AC-6 (`sdd/01_planning/01_feature/acorn_feature_spec.md`) 전부 테스트 통과.
- 회귀(미니홈피 인벤토리 조회) green. proof 게이트 exit 0 = 완료.

## Execution Checklist (비중첩)
- [x] T1 @backend-dev  충전(가상 결제 스텁) + order_id 멱등 처리 (`server/contexts/acorn/service.py`)
- [x] T2 @backend-dev  아이템 구매(잔액 부족 거부 + order_id 멱등 + 인벤토리 추가)
- [x] T3 @backend-dev  선물(양도) 처리(잔액 초과 거부 포함)
- [x] T4 @backend-dev  거래내역(ledger) 기록 + 조회 API(`ledger_for`)
- [x] T5 @test-dev     proof 게이트 (`tests/test_acorn.py`) — AC-1~AC-6 전부 커버

## Regression Scope
- direct: 충전·구매·선물·거래내역
- shared: 미니홈피 스킨/BGM 적용(`server/contexts/minihomepy`)이 조회하는 인벤토리 인터페이스
- 근거: `sdd/02_plan/10_test/regression_verification.md`

## Current Notes
- 2026-07-02 @backend-dev 요청으로 충전+구매 슬라이스(AC-1~AC-4) 구현. 인벤토리 조회
  인터페이스(`inventory` dict)는 확정되어 minihomepy T4가 이를 참조할 수 있다.
- 2026-07-02 @backend-dev 요청으로 선물·거래내역(AC-5·AC-6)까지 구현 완료. `gift()`는
  charge/purchase와 동일한 order_id 멱등 패턴을 재사용했고, `ledger`에 모든 증감이
  기록되어 `ledger_for(user)`로 조회할 수 있다.
- 잔액부족으로 거부된 order_id는 idempotency 캐시에 결과가 남는다: 같은 order_id로
  충전 후 재시도해도 재검증 없이 동일 거부가 반환된다(의도적 단순화, 잔액부족 후 재시도는
  새 order_id 사용 전제). `sdd/04_verify/01_feature/acorn.md`에 residual risk로 기록.

## Validation
- `python3 proof/run_proof.py` → 32/32 PASS (exit 0), `tests/test_acorn.py` 9건 포함
  (`sdd/04_verify/01_feature/acorn.md`, `tmp/proof-results.json`, 2026-07-02).

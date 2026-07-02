# 도토리(ACORN) · 검증 (retained)

> proof: `python3 proof/run_proof.py` → 32/32 PASS (exit 0), 그 중 ACORN 9건.
> 실행: Python 3.14.6, `tmp/proof-results.json` (2026-07-02).

| 분면 | 검증 대상 | 수용기준 | 결과 |
| --- | --- | --- | --- |
| 기능 | 충전 후 잔액 반영 | AC-1 | PASS · `test_charge_updates_balance` |
| 멱등 | 같은 order_id 충전 재실행 시 중복 없음 | AC-2 | PASS · `test_charge_idempotent_same_order` |
| 검증 | 잔액 부족 시 구매 거부(인벤토리 미반영) | AC-3 | PASS · `test_purchase_rejected_when_balance_insufficient` |
| 기능 | 구매 성공 시 잔액 차감 + 인벤토리 반영 | AC-4 | PASS · `test_purchase_succeeds_and_updates_inventory` |
| 멱등 | 같은 order_id 구매 재실행 시 중복 차감 없음 | AC-2 | PASS · `test_purchase_idempotent_same_order` |
| 기능 | 선물 시 양쪽 잔액 갱신(차감/증가) | AC-5 | PASS · `test_gift_transfers_balance` |
| 검증 | 보유 잔액 초과 선물 거부 | AC-6 | PASS · `test_gift_rejected_when_exceeds_balance` |
| 멱등 | 같은 order_id 선물 재실행 시 중복 이체 없음 | AC-2·AC-5 | PASS · `test_gift_idempotent_same_order` |
| 거래내역 | 충전·구매·선물이 양쪽 ledger에 순서대로 기록 | (요구사항: 모든 증감 기록) | PASS · `test_ledger_records_all_movements` |

## Residual Risk
- 없음(계획된 AC-1~AC-6 전부 구현·검증 완료).
- 잔액 부족으로 거부된 order_id는 멱등 캐시에 남아, 이후 잔액을 채운 뒤 같은 order_id로
  재시도해도 재검증 없이 동일 거부가 반환된다(`sdd/03_build/01_feature/acorn.md` 참고).
  실 결제/선물 재시도는 새 order_id 발급을 전제로 설계했다 — 이 전제가 맞지 않으면 별도
  AC로 정제 필요.

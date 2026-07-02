# 투데이(TODAY) · 검증 (retained)

> proof: `python3 proof/run_proof.py` → 12/12 PASS (exit 0), 그 중 TODAY 3건.
> 실행: Python 3.14.6, `tmp/proof-results.json` (2026-07-02).

| 분면 | 검증 대상 | 수용기준 | 결과 |
| --- | --- | --- | --- |
| 기능 | 하루 첫 등록 시 recorded | AC-1 | PASS · `test_check_in_first_time` |
| 멱등 | 같은 날 재요청 시 already | AC-2 | PASS · `test_check_in_idempotent_same_day` |
| 기능 | 날짜 변경 후 재등록 허용 | AC-3 | PASS · `test_check_in_new_day_allowed` |

## Residual Risk
- 없음(3개 AC 전부 구현·검증 완료).

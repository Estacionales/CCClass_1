# Proof 증거 (retained)

게이트: `python3 proof/run_proof.py` (= contract.json `commands.proof`)

```
14 passed in 0.02s
[proof] PASS · 14/14 passed → tmp/proof-results.json
```

| 테스트 | AC | 결과 |
| --- | --- | --- |
| test_ac1_issue_after_consent | AC-1 | PASS |
| test_ac1_reject_without_consent | AC-1 | PASS |
| test_ac2_retry_circuit_fallback | AC-2 | PASS |
| test_ac2_recovers_on_late_success | AC-2 | PASS |
| test_ac3_citation_path_is_exact | AC-3 | PASS |
| test_ac3_advisory_exactness | AC-3 | PASS |
| test_ac3_guardrail_refuses_when_ineligible | AC-3 | PASS |
| test_ac4_issue_is_idempotent | AC-4 | PASS |
| test_ac4_settlement_no_duplicate | AC-4 | PASS |
| test_ac5_withdraw_stops_processing | AC-5 | PASS |
| test_ac5_ledger_is_append_only | AC-5 | PASS |
| test_regression_other_minwon_eligibility | 회귀 | PASS |
| test_regression_unknown_minwon_is_blocked | 회귀 | PASS |
| test_regression_settlement_totals | 회귀 | PASS |

> 머신·산출 JSON은 `tmp/proof-results.json`(빌드 시 생성)에서 재확인 가능.

# 회귀 검증 범위 (retained)

> SKILL.md §3 — 회귀 표면 선정은 유지 아티팩트다. 새 기능(direct)만이 아니라
> 영향받는 공유 표면(shared)까지 함께 green이어야 완료.

| 표면 | 분류 | 검증 |
| --- | --- | --- |
| 발급 오케스트레이션 | direct | `test_ac1_*`, `test_ac4_issue_is_idempotent` |
| 자격검증·근거 규칙 | shared | `test_regression_other_minwon_eligibility`, `test_regression_unknown_minwon_is_blocked` |
| 정산 합계 | shared | `test_regression_settlement_totals`, `test_ac4_settlement_no_duplicate` |
| 동의 원장(append-only) | shared | `test_ac5_ledger_is_append_only` |
| 근거 인용 정확성 | direct | `test_ac3_*` + `run_citation_check.py` |

선정 근거: 발급 흐름이 `server/shared/*`(rules·eligibility·consent_ledger)와 정산을
공유하므로, 해당 공유 모듈을 건드린 변경은 회귀 범위를 그 표면까지 넓힌다.

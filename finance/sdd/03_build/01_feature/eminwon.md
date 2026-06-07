# 전자민원 발급 · current-state

> 03_build: dated 로그가 아니라 '지금 이렇게 떠 있다' 한 벌(Overwrite Rule).

## Absorbed Planning
- `01_planning/01_feature/eminwon_issue.md` (EARS AC-1~AC-5)
- `02_plan/01_feature/eminwon_todos.md` (T1~T4 비중첩)

## Runtime Assembly (entry → orchestrator → leaf)
- entry: `IssueOrchestrator.issue(user_id, minwon_type, responder)`
  → `server/contexts/eminwon/issue_svc.py`
- 흐름:
  1. `consent.is_active(user)` 동의 게이트 (AC-1)
  2. `rules.trace(minwon)` 근거 경로 + `eligibility.is_eligible` 가드레일 (AC-3)
  3. `eligibility.required_documents(minwon)` 서류 산출
  4. `adapter.collect(doc, responder)` 기관 수집 (AC-2 회복력)
  5. `IdempotencyStore.issue_once(key, …)` 멱등 발급 (AC-4)

## Modules (구현)
| 모듈 | 책임 | AC |
| --- | --- | --- |
| `contexts/eminwon/issue_svc.py` | 발급 오케스트레이션·동의게이트·파기 | 1·3·5 |
| `contexts/eminwon/idem.py` | idempotency_key(SHA256) + dedup | 4 |
| `integration/adapters/gw/base_adapter.py` | 재시도3·서킷·대체 경로 | 2 |
| `contexts/settlement/batch.py` | 정산 배치 멱등 | 4 |
| `contexts/advisory/citation.py` | 근거 여러 단계 인용·거부 | 3 |
| `shared/{consent_ledger,eligibility,rules}.py` | 공유 계약 | 1·3·5 |

## Contracts
- `consent_ledger`: 부여·철회·만료 append-only
- `gw.adapter`: retry3 · circuit_breaker · fallback_route
- `rules`: 민원→서류→규정→예외 결정적 그래프

## Current Behavior
동의 확인 → 자격·근거 가드레일 → 서류 산출 → 기관 수집(무응답 시 대체경로) →
멱등 발급. 동의 철회 시 처리 중단·파기·원장 기록.

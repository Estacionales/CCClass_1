# 전자민원 발급 · todos (비중첩 작업 분할)

EARS 다섯 줄을 할 일로 펴고, 파일·계약이 겹치지 않게 나눈다. 영역이 안 겹쳐야
여러 에이전트를 동시에 돌려도 충돌이 없다.

- [x] T1 @backend-dev  발급 오케스트레이션 + 멱등키 (AC-1·AC-4)
- [x] T2 @연계-dev     기관 어댑터 + 회복력 정책 (AC-2)
- [x] T3 @정산-dev     발급 수수료 정산 배치 멱등 처리 (AC-4)
- [x] T4 @상담-dev     근거 규정 인용 응답 (AC-3)

## 비중첩 경계 (서로 다른 leaf만 만짐 → 병렬 안전)

| 작업 | 소유 경로 |
| --- | --- |
| T1 | `server/contexts/eminwon/*` (오케스트레이션·멱등) |
| T2 | `server/integration/adapters/gw/*` (연계 게이트웨이) |
| T3 | `server/contexts/settlement/*` (정산) |
| T4 | `server/contexts/advisory/*` (상담·근거 인용) |
| 공유 | `server/shared/*` (consent_ledger·eligibility·rules) — cross-cutting, T1 소유 |

> 동의 철회(AC-5)는 네 영역에 걸치는 cross-cutting이라 공유 계약(`consent_ledger`)으로
> 빼서 T1(오케스트레이터)이 소유한다.

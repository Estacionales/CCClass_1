# realprice_ingest · 작업 계획 개요 (02_plan/01_feature)

> SDD 'plan' 산출물. `01_planning/03_architecture/realprice_architecture.md`의 경계 결정(D-1~D-6)을
> 따라 구현 작업을 T1~T4 + common 5개 트랙으로 나눈다. 각 트랙은 서로 다른 모듈만 건드리도록 설계해
> 병렬로 진행할 수 있게 한다. 개별 트랙 계획은 아래 파일이 정본이다.

| 트랙 | 계획 파일 | 소유 에이전트 | 건드리는 모듈(디렉터리) |
| --- | --- | --- | --- |
| 공유 계약 | `01_common_contract.md` | `backend-dev` | `common/**` (단독 쓰기 권한) |
| T1 수집 | `02_t1_ingestion.md` | `ingestion-dev` | `ingestion-service/**` |
| T2 거래원장 | `03_t2_transaction.md` | `transaction-dev` | `transaction-service/**` |
| T3 분석 | `04_t3_analytics.md` | `analytics-dev` | `analytics-service/**` |
| T4 플랫폼 | `05_t4_platform.md` | `platform-dev` | `service-discovery/**`, `config-server/**`, `api-gateway/**` |

## 모듈 비중첩 원칙 (No Overlap)

- 각 트랙은 위 표의 자기 디렉터리만 수정한다. 다른 트랙의 모듈을 수정해야 할 필요가 생기면(예:
  DTO 필드 추가) 해당 변경은 트랙 작업이 아니라 `common` 소유자(`backend-dev`)에게 계약 변경으로
  요청한다 — 직접 편집하지 않는다.
- `common`은 5개 트랙 중 유일하게 다른 모든 트랙이 의존하는 공유 라이브러리다(D-4, `run_arch_check.py`
  규칙 2·3). 여러 트랙이 동시에 `common`을 건드리면 병렬 작업의 전제(모듈 비중첩)가 깨지므로,
  `common`의 쓰기 권한은 `backend-dev` 단독으로 둔다. T1/T2/T3/T4는 `common`이 게시한 공개 API를
  **소비만** 한다.
- `config-server`가 들고 있는 `ingestion-service`용 설정 파일(`config-server/src/main/resources/config/ingestion-service.yml`)은
  물리적으로 T4 모듈 안에 있지만 내용은 T1의 런타임 동작(엔드포인트 경로)에 영향을 준다. 이 파일은
  T4(`platform-dev`)가 수정하되, `01_planning/07_integration/molit_integration.md` §1의 확정 값을
  근거로 하며 T1과 사전 합의된 값만 반영한다(§ T4 계획의 공유 파일 경계 항목 참조).

## 시퀀싱 (Phase 0 → 병렬)

```text
Phase 0 (선행, backend-dev)         Phase 1 (Phase 0 완료 후 T1~T3 병렬, T4는 즉시 병렬)
──────────────────────────          ─────────────────────────────────────────────────
common 공개 API 확정                  T1 ingestion-service  ─┐
(AptTransactionDto,                  T2 transaction-service ─┼─ 서로 다른 모듈, 동시 진행 가능
DealAmountNormalizer,                T3 analytics-service   ─┘
CancelStatusResolver,
MolitDateParser,                     T4 platform (T2 API 컨트랙트만 알면 되므로 즉시 시작 가능,
AptTransactionNaturalKey)            common 의존 없음)
```

- T1·T2·T3는 `common`의 공개 API가 컴파일 가능한 형태로 존재해야 각자 모듈을 빌드할 수 있다
  (`build.gradle`에 이미 `implementation project(':common')`이 선언되어 있음). 따라서 Phase 0을
  먼저 완료하거나, 최소한 인터페이스 시그니처를 프리즈한 뒤 Phase 1을 시작한다.
- T4는 `common`에 의존하지 않는다(구조 게이트 규칙 2·3 대상이 아님) — Phase 0을 기다리지 않고 바로
  시작할 수 있다. 단, T1이 정의하는 `POST /internal/transactions/batch-upsert` 호출 경로와 T2의
  게이트웨이 라우트 존재 여부(구조 게이트 규칙 4)는 `05_api/realprice_api.md`가 이미 확정했으므로
  T4는 그 계약을 그대로 라우팅 설정에 반영하면 된다.

## 트랙 간 계약 참조 (편집 없이 읽기만)

| 트랙 | 참조해야 하는 다른 트랙의 계약 | 정본 문서 |
| --- | --- | --- |
| T1 | T2가 노출할 적재 API 형태 | `05_api/realprice_api.md` §3b |
| T2 | (없음 — 원장은 하류에 의존하지 않음) | - |
| T3 | T2가 노출하는 조회 API 형태 | `05_api/realprice_api.md` §3 |
| T4 | T1/T2/T3가 노출하는 게이트웨이 라우트 3종 | `05_api/realprice_api.md` §2, §3, §4 |

## 전체 Acceptance Criteria (트랙 통합 기준)

- AC-1~AC-5는 `01_planning/01_feature/realprice_ingest.md`가 정본이며, 각 트랙 계획의 AC는 이를
  트랙 범위로 좁힌 부분집합이다.
- 트랙별 구현이 끝나도 `run_arch_check.py`(구조 게이트) + `./gradlew test`가 모두 통과해야
  `02_plan/01_feature` 전체를 완료로 본다(개별 트랙 완료 ≠ 전체 완료).

## 회귀 범위 (전체 통합 시점)

- 직접: `common`, `ingestion-service`, `transaction-service`, `analytics-service`, `api-gateway`,
  `config-server`, `service-discovery` 전체(신규 구현이므로 사실상 전 모듈).
- 상류/하류: T1→T2(batch-upsert), T3→T2(조회), gateway→T1/T2/T3(라우팅) — 트랙 간 계약이 상호
  상류/하류 관계다.
- 공유: `common` 공개 API, `api-gateway` 라우팅, `config-server` 설정 경계.
- 정당화된 제외: 없음(그린필드 최초 구현이라 전체가 회귀 대상).

## Execution Checklist (개요 레벨)

- [ ] Phase 0 — `01_common_contract.md` 완료(공개 API 확정)
- [ ] Phase 1 — T1~T4 병렬 구현(각 트랙 파일의 체크리스트)
- [ ] 통합 — `run_arch_check.py` + `./gradlew test` 전체 통과 확인
- [ ] `sdd/03_build/01_feature`에 구현 요약 기록
- [ ] `sdd/04_verify/01_feature`에 회귀 검증 증거 기록

## Current Notes

- 2026-07-02: 트랙 분리·common 소유자(backend-dev) 확정. 아직 코드 구현 착수 전(스캐폴드만 존재).

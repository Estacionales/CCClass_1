# T2 · 거래원장(transaction-service) · 작업 계획

> SDD 'plan' 산출물. 대상 위치: `sdd/02_plan/01_feature/03_t2_transaction.md`
> 소유 에이전트: `transaction-dev`. 건드리는 모듈: `transaction-service/**`만. `common/**`은 소비만
> 하고 직접 수정하지 않는다.

## Scope
- 변경 대상 모듈: `transaction-service/**`.
- 범위 밖: `common`(계약 변경은 `01_common_contract.md` 담당), `ingestion-service`(호출자 구현은 T1
  담당, T2는 계약만 제공), `analytics-service`(호출자 구현은 T3 담당).

## Assumptions
- 환경: DEV(개발계)
- 의존/선결 조건: `01_common_contract.md`(Phase 0) 공개 API 확정. T2는 다른 트랙의 구현 완료를
  기다릴 필요가 없다 — 거래원장은 T1(상류)·T3(하류) 어느 쪽에도 의존하지 않는 독립 모듈이다
  (`00_overview.md` 트랙 간 계약 참조표: T2 행이 "없음").

## Acceptance Criteria
- AC-1: `AptTransaction` 엔티티가 `04_data` §1.1 필드 전체를 저장한다.
- AC-1/AC-4: 자연키(`04_data` §1.2, 9개 필드) 복합 유니크 제약, upsert 시 충돌 건은 갱신·비충돌 건은 신규 생성.
- AC-3: `canceled`/`canceledDate` 저장, 삭제 없이 이력 보존(DAR-005) — 조회 API는 `canceled` 값과
  무관하게 전체 반환(집계 제외는 T3 책임).
- `GET /api/v1/transactions`가 `05_api` §3 스키마·페이징을 만족한다.
- `POST /internal/transactions/batch-upsert`가 `05_api` §3b 스키마(`receivedCount`, `createdCount`,
  `updatedCount`)를 만족한다.

## 모듈 의존 그래프
```
common ──→ transaction-service
             ↑ (호출자: ingestion-service, analytics-service — 둘 다 T2 코드 안에 있지 않음)
```

## 런타임 흐름 (end-to-end)
```
POST /internal/transactions/batch-upsert (T1이 호출)
  → 자연키로 기존 행 조회 → 있으면 갱신, 없으면 생성 → 건수 집계 응답

GET /api/v1/transactions?sggCd=&dealYm= (via api-gateway, T3/최종 클라이언트가 호출)
  → sggCd+dealYm 조건 페이징 조회 → AptTransaction 목록 반환(canceled 포함)
```

## 회귀 범위 (regression scope)
- 직접: `transaction-service/**`.
- 상류: `ingestion-service`가 호출하는 `batch-upsert` 계약(T1 구현과 별개로, 계약 스펙 자체는 T2가
  통제). 계약을 바꾸면 T1에 통지.
- 하류: 없음(T2는 다른 서비스를 호출하지 않는 write model 종단).
- 공유: `common`(자연키·DTO 소비), `api-gateway`의 `/api/v1/transactions/**` 라우트(T4가 존재 확인).
- 정당화된 제외: `ingestion-service`/`analytics-service` 내부 구현(각자 트랙 회귀 범위).

## Execution Checklist
- [ ] `AptTransaction` JPA 엔티티(`04_data` §1.1 필드) + 자연키 9개 컬럼 복합 유니크 제약
- [ ] Repository: 자연키 기준 존재 조회 + upsert(트랜잭션 단위)
- [ ] `POST /internal/transactions/batch-upsert` 컨트롤러(`05_api` §3b, 최대 1000건 배치)
- [ ] `GET /api/v1/transactions` 컨트롤러(`05_api` §3, `sggCd`+`dealYm` 필수 파라미터, 페이징, 정렬)
- [ ] `canceled`/`canceledDate` 컬럼 매핑, 재수집 시 정상→해제 전환 반영(CONR-005) 테스트
- [ ] 단위 테스트: 자연키 충돌 시 갱신, 비충돌 시 생성, 동시 재수집 시 중복 미생성(AC-4)
- [ ] H2 스캐마(`ddl-auto: create-drop`) 학습용 제약을 `03_build`에 현재 상태로 기록(운영 전환 시
      마이그레이션 필요 — 본 트랙 범위 밖, 후속 과제로만 남김)

## Current Notes
- 2026-07-02: 계획 수립. 구현 착수 전.

## Validation (proof 게이트)
- `./gradlew :transaction-service:test` exit 0
- `python3 sdd/99_toolchain/01_automation/run_arch_check.py` exit 0 (규칙 3 "transaction-service → common 의존")

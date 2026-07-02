# T1 · 수집(ingestion-service) · 작업 계획

> SDD 'plan' 산출물. 대상 위치: `sdd/02_plan/01_feature/02_t1_ingestion.md`
> 소유 에이전트: `ingestion-dev`. 건드리는 모듈: `ingestion-service/**`만. `common/**`은 소비만
> 하고 직접 수정하지 않는다(변경 필요 시 `backend-dev`에 요청).

## Scope
- 변경 대상 모듈: `ingestion-service/**`.
- 범위 밖: `common`(계약 변경은 `01_common_contract.md` 담당), `transaction-service`(적재 API 자체
  구현은 T2 담당, T1은 그 계약을 호출만 함), config-server의 `ingestion-service.yml`(파일 소유는 T4,
  §공유 파일 경계 참조).

## Assumptions
- 환경: DEV(개발계)
- 의존/선결 조건: `01_common_contract.md`(Phase 0) 공개 API 확정. `05_api/realprice_api.md` §3b
  (`POST /internal/transactions/batch-upsert`)가 T2 쪽 계약으로 이미 확정되어 있어, T2 구현 완료를
  기다리지 않고 그 계약대로 클라이언트 코드를 먼저 작성할 수 있다(계약 우선 병렬화).

## Acceptance Criteria
- AC-1: `getRTMSDataSvcAptTradeDev` 상세 엔드포인트 호출, `totalCount` 기준 전량 페이징(SFR-001, SFR-002).
- AC-2: resultCode 매트릭스(`07_integration` §3) 분기, resilience4j 재시도·서킷(§4) 적용, 일부 실패 시
  나머지 구간 계속 진행(SFR-011).
- AC-3: `common`의 `DealAmountNormalizer`/`CancelStatusResolver`/`MolitDateParser`로 정규화, 품질 게이트
  위반 건 스킵·사유 기록(데이터명세서 §5).
- AC-4: 동일 `sggCd`+`dealYm` 재호출 시 T2의 upsert 계약을 그대로 재사용(멱등성은 T2 책임, T1은 중복
  판정 로직을 갖지 않음).
- `POST /api/v1/ingest/jobs` 응답이 `05_api/realprice_api.md` §2 스키마(`totalCount`, `pagesFetched`,
  `upsertedCount`, `skippedCount`, `skippedReasons`, `partial`)를 만족한다.

## 모듈 의존 그래프
```
common ──→ ingestion-service ──(WebClient, lb://transaction-service)──→ POST /internal/transactions/batch-upsert
```

## 런타임 흐름 (end-to-end)
```
POST /api/v1/ingest/jobs (via api-gateway)
  → ingestion-service: molit 호출(페이징) → XML 파싱 → common 정규화
  → 최대 1000건 배치로 transaction-service.batch-upsert 호출
  → 집계 응답(upsertedCount/skippedCount) 반환
```

## 회귀 범위 (regression scope)
- 직접: `ingestion-service/**`.
- 상류: `api-gateway`의 `/api/v1/ingest/**` 라우트(T4가 이미 정의, 변경 없음 — 존재만 확인).
- 하류: `transaction-service`의 `batch-upsert` 계약(§05_api §3b, 구현은 T2). T1은 계약 스펙대로
  클라이언트를 만들고, 통합 테스트는 T2 완료 후 재확인.
- 공유: `common` 공개 API(소비), `config-server`의 `molit.*` 설정 키(값은 T4가 관리, T1은 키 이름만 참조).
- 정당화된 제외: `transaction-service` 내부 구현 세부(T2 회귀 범위).

## Execution Checklist
- [x] `ingestion-service/src/main/resources/application.yml`의 로컬 기본값
      `molit.apt-trade-path`를 상세(Dev) 엔드포인트로 정정(`07_integration` §1 드리프트 정정)
- [x] molit API 클라이언트 구현(WebClient + `jackson-dataformat-xml`, `MolitApiClient`) — 단일 페이지
      호출까지. 전량 페이징 루프는 별도 항목(아래, 미착수)
- [ ] 페이징 전량 수집 루프(`totalCount` 기준 종료 판정) — 미착수
- [ ] resultCode 분기 처리(`07_integration` §3 매트릭스: 000/03/01·04·99/12/20/22/30/31/32) — 미착수.
      현재는 fetch 성공/실패(재시도·서킷 소진)만 `MolitFetchResult`로 구분, resultCode별 세부 분기 없음
- [x] resilience4j retry(`max-attempts=3`, `wait-duration=500ms`) + circuitbreaker(`sliding-window-size=20`,
      `failure-rate-threshold=50`, `wait-duration-in-open-state=10s`) 적용 확인 — `@Retry`/`@CircuitBreaker`
      + fallback(`fetchPageFallback`) 구현, config-server 기존 정책값과 이름(`molitApi`) 일치
- [ ] 동시성 제한(시군구 단위 세마포어 5) + 트래픽초과(22) 백오프·이월(`07_integration` §5) — 미착수
- [x] `common` 유틸로 필드 정규화 → 매핑 — 계획의 `AptTransactionDto`가 아니라 pin 테스트가 고정한
      `common.AptTransaction`(11필드)으로 매핑(`AptTransactionNormalizer`). 품질 게이트 위반(금액 파싱
      실패·면적 0 이하)은 `IllegalArgumentException`으로 스킵 신호
- [ ] `transaction-service`의 `POST /internal/transactions/batch-upsert` 클라이언트 호출 — 미착수
- [ ] `POST /api/v1/ingest/jobs` 컨트롤러(`05_api` §2 요청/응답 스키마) — 미착수
- [x] 단위 테스트 — `DealAmountParserTest`(common), `AptTransactionNormalizerTest`(ingestion-service) 확장,
      `./gradlew :common:test :ingestion-service:test` BUILD SUCCESSFUL. XML 파싱·resultCode 분기 자체
      단위테스트는 그 기능이 아직 없어 해당 없음. T2 완료 후 통합 테스트는 미착수

## Current Notes
- 2026-07-02: 계획 수립. 구현 착수 전.
- 2026-07-02: `MolitApiClient`(단일 페이지 + resilience4j)·`AptTransactionNormalizer`·엔드포인트 드리프트
  정정 구현 완료(ingestion-dev). 진행 중 `common.AptTransaction`을 14필드로 잘못 만들어
  `transaction-service`/`analytics-service`의 기존 pin 테스트 컴파일을 깼던 것을 오케스트레이션 세션에서
  11필드로 재작성해 바로잡음(`03_build/01_feature/02_t1_ingestion.md` 참조). 페이징 루프·잡 컨트롤러·
  batch-upsert 클라이언트·동시성 제한은 다음 이터레이션.

## Validation (proof 게이트)
- `./gradlew :ingestion-service:test` exit 0
- `python3 sdd/99_toolchain/01_automation/run_arch_check.py` exit 0 (규칙 3 "ingestion-service → common 의존")

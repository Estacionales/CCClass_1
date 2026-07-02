# T3 · 분석(analytics-service) · 작업 계획

> SDD 'plan' 산출물. 대상 위치: `sdd/02_plan/01_feature/04_t3_analytics.md`
> 소유 에이전트: `analytics-dev`. 건드리는 모듈: `analytics-service/**`만. `common/**`은 소비만
> 하고 직접 수정하지 않는다.

## Scope
- 변경 대상 모듈: `analytics-service/**`.
- 범위 밖: `common`(계약 변경은 `01_common_contract.md` 담당), `transaction-service`(조회 API 구현은
  T2 담당, T3는 그 계약을 호출만 함).

## Assumptions
- 환경: DEV(개발계)
- 의존/선결 조건: `01_common_contract.md`(Phase 0) 공개 API 확정. `05_api/realprice_api.md` §3
  (`GET /api/v1/transactions`)이 T2 쪽 계약으로 이미 확정되어 있어, T2 구현 완료를 기다리지 않고 그
  계약대로(mock 서버 또는 계약 테스트) 클라이언트·집계 로직을 먼저 작성할 수 있다.

## Acceptance Criteria
- AC-3: `canceled=true` 거래를 집계에서 제외한다(DAR-005, D-2 CQRS 분리).
- AC-5: `GET /api/v1/market-stats`가 `05_api` §4 스키마(`transactionCount`, `medianDealAmountWon`,
  `medianPricePerArea`, `computedAt`)를 만족한다.
- PER-001: 응답 P99 300ms 이내 목표(사전 산출/캐시된 read model에서 조회, 조회 시점 실시간 재집계 금지).
- PER-003: 원장 쓰기 부하와 통계 조회 부하가 격리된다(별도 read model, D-2/D-3 근거).

## 모듈 의존 그래프
```
common ──→ analytics-service ──(WebClient, lb://transaction-service)──→ GET /api/v1/transactions
```

## 런타임 흐름 (end-to-end)
```
(산출 경로) analytics-service → transaction-service.GET /api/v1/transactions?sggCd=&dealYm= 호출
  → canceled=false 필터 → dealAmountWon/pricePerArea 중위값 계산 → MarketStat 저장

(조회 경로) GET /api/v1/market-stats (via api-gateway) → analytics-service의 저장된 MarketStat 반환
```

## 회귀 범위 (regression scope)
- 직접: `analytics-service/**`.
- 상류: `api-gateway`의 `/api/v1/market-stats/**` 라우트(T4가 존재 확인).
- 하류: `transaction-service`의 `GET /api/v1/transactions` 계약(§05_api §3, 구현은 T2). T3는 계약
  스펙대로 클라이언트를 만들고, 통합 테스트는 T2 완료 후 재확인.
- 공유: `common` 공개 API(소비).
- 정당화된 제외: `transaction-service` 내부 구현 세부(T2 회귀 범위).

## Execution Checklist
- [ ] `transaction-service` 조회 클라이언트 구현(WebClient, `lb://transaction-service`)
- [ ] `MarketStat` 저장 모델(`04_data` §2.1: `sggCd`, `dealYearMonth`, `transactionCount`,
      `medianDealAmountWon`, `medianPricePerArea`, `sourceTransactionCount`, `computedAt`)
- [x] 집계 로직: `canceled=false` 필터 → 정렬 → 중위값(홀수/짝수 분기) 계산
- [ ] `GET /api/v1/market-stats` 컨트롤러(`05_api` §4)
- [ ] 산출 트리거 설계(수집 완료 후 즉시 재산출 vs 조회 시점 캐시 미스 시 산출 — 결정하고 Current Notes에 기록)
- [x] 단위 테스트: 중위값 경계 케이스(짝수/홀수 건수), 해제 거래 제외 검증(AC-3), 집계 대상 0건(빈 통계) 케이스
- [ ] PER-001 목표 확인을 위한 최소 응답시간 측정(부하테스트 또는 벤치마크 스크립트)

## Current Notes
- 2026-07-02: 계획 수립. 구현 착수 전. 산출 트리거 방식(즉시 재산출 vs 캐시)은 구현 시점에 결정.
- 2026-07-02: 도메인 집계 슬라이스 구현. `MarketStatCalculator`(해제 제외 → 중위 거래금액/중위 ㎡당 단가,
  결정적) + read model `MarketStat`을 pin 테스트/instructor reference 계약대로 작성. `analytics-service:test`
  green(3케이스), arch-check 7/7. 구현 상세·계약 드리프트는 `03_build/01_feature/04_t3_analytics.md` 참조.
  아직 미착수(다음 슬라이스): transaction-service 조회 클라이언트, `GET /api/v1/market-stats` 컨트롤러,
  `@SpringBootApplication` 부트스트랩, 산출 트리거 결정, `MarketStat` 지속화, PER-001/PER-003 측정.
  read model 형태는 `04_data §2.1` 계획 필드명과 다르다(pin 테스트/ reference 정본 채택) — 정합 조정은 후속 판단.
- 단위 테스트 항목 체크: `MarketStatCalculatorTest`는 이미 커밋되어 있던 pin 테스트이며(신규 저작 아님),
  이번 구현에 대해 홀수/짝수(해제 제외)/빈 입력 3케이스가 green으로 확인됐다.

## Validation (proof 게이트)
- `./gradlew :analytics-service:test` exit 0
- `python3 sdd/99_toolchain/01_automation/run_arch_check.py` exit 0 (규칙 5 "analytics가 transaction 조회, CQRS 분리")

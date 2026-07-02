# T3 · 분석(analytics-service) read model 슬라이스 · 구현 요약 (03_build)

> SDD 'build' 산출물. current-state only — dated execution narrative 금지.
> 대상 위치: `sdd/03_build/01_feature/04_t3_analytics.md`

## 구현 범위
- 구현한 기능/경계:
  - `analytics-service` 순수 도메인 집계(read model): 거래 목록에서 시세 통계를 계산하는
    `MarketStatCalculator`와 그 결과 read model `MarketStat`.
  - AC-3(해제 제외): `canceled=true` 거래를 집계 대상에서 완전히 제외한다.
  - AC-5(CQRS read): 거래원장 원본이 아니라 조회 최적화된 집계 결과(`MarketStat`)만 노출한다.
    거래원장에 쓰지 않고(읽기 전용) 중위 거래금액·중위 ㎡당 단가만 산출한다.
  - 결정성(정합): 정렬 기반 중위값이라 같은 입력 → 같은 통계(부동소수 누적 없음, `long` 정수 연산).
- 이 슬라이스는 도메인 로직만이다. HTTP 조회 클라이언트·REST 컨트롤러·부트스트랩은 이번 턴 범위 밖(아래 참조).

## 변경 모듈
- analytics-service (이 슬라이스로 최초의 메인 소스가 생겼다):
  - `kr.elice.realfield.analytics.domain.MarketStat` — 시세 통계 read model record. **6필드**
    (`sggCd, dealYear, dealMonth, tradeCount, medianPriceWon, medianPricePerM2Won`) +
    정적 팩터리 `empty(sggCd, dealYear, dealMonth)`(0으로 채운 통계 반환).
  - `kr.elice.realfield.analytics.domain.MarketStatCalculator` — `@Component`,
    `MarketStat calculate(String sggCd, int dealYear, int dealMonth, List<AptTransaction> transactions)`.
    `canceled` 필터 → `dealAmountWon`·`pricePerSquareMeter()` 각각 정렬 후 중위값 계산 →
    유효 거래가 0건이면 `MarketStat.empty(...)` 반환. private `median(long[])`이 홀수/짝수 분기를 담당.
  - `build.gradle` 변경 없음(`:common` + `spring-boot-starter-web`가 이미 있어 `@Component` 사용에 충분,
    이 도메인 슬라이스는 webflux/loadbalancer 의존을 실제로 쓰지 않는다).
- common: 소비만 함(수정 없음). `AptTransaction`(11필드 record)의 `canceled()`, `dealAmountWon()`,
  `pricePerSquareMeter()` 계약을 그대로 사용한다. ㎡당 단가 계산식은 재구현하지 않고
  `common.AptTransaction.pricePerSquareMeter()`(면적 0 이하 → 0)에 위임한다.

## 계약·자산
- read model 계약(최종, 이번 슬라이스): `MarketStat(sggCd, dealYear, dealMonth, tradeCount,
  medianPriceWon, medianPricePerM2Won)`. 이 형태는 저장소에 이미 커밋되어 있던 pin 테스트
  `analytics-service/MarketStatCalculatorTest`와 instructor reference
  (`solution/analytics-service/.../domain/{MarketStat,MarketStatCalculator}.java`)가 고정한 계약을
  정본으로 따랐다. pin 테스트는 `tradeCount()`·`medianPriceWon()` 두 접근자만 검사하지만, reference와
  동일하게 `medianPricePerM2Won`(중위 ㎡당 단가)까지 채워 완전한 read model을 제공한다(세 번째 필드는
  pin 테스트와 충돌하지 않는다 — 테스트가 검사하지 않을 뿐).
- 중위/제외 로직(결정적):
  - 제외: `transactions.stream().filter(t -> !t.canceled())`. 해제거래는 건수에도 중위 계산에도 들어가지 않는다.
  - 중위: 값 배열을 오름차순 정렬 후 `n`이 홀수면 `sorted[n/2]`, 짝수면 `(sorted[n/2-1] + sorted[n/2]) / 2`.
    금액·㎡단가 각각 같은 방식으로 계산한다. `long` 정수 나눗셈이라 짝수 평균은 내림(예: (700M+800M)/2=750M).
  - 빈 입력·전건 해제: 필터 후 비면 `MarketStat.empty(...)` → `tradeCount()==0`, `medianPriceWon()==0L`
    (예외/`null` 아님).
- 계획 대비 드리프트(read model 형태): 계획서(`02_plan/01_feature/04_t3_analytics.md` 체크리스트,
  `04_data §2.1`)가 그린 저장 모델 필드(`dealYearMonth`, `transactionCount`, `medianDealAmountWon`,
  `medianPricePerArea`, `sourceTransactionCount`, `computedAt`)와 실제 구현 형태가 다르다:
  - `dealYear`+`dealMonth`(분리) vs 계획의 `dealYearMonth`(결합).
  - `tradeCount` vs `transactionCount`, `medianPriceWon` vs `medianDealAmountWon`,
    `medianPricePerM2Won` vs `medianPricePerArea`.
  - `sourceTransactionCount`·`computedAt`(시스템/집계 메타)은 이번 read model에 없다.
  - 지속화(store/repository)도 아직 없다(현재는 순수 도메인 값 객체).
  이 축소·명명 차이는 pin 테스트/instructor reference를 정본으로 삼은 결과이며 의도적이다. 계획서의
  `04_data §2.1` 필드 표를 이 계약에 맞춰 갱신할지, 저장/조회 슬라이스 구현 시 필드를 보강할지는
  사용자/오케스트레이션 판단이 필요하다(아직 하지 않음).

## 현재 사용자 가시 동작
- 외부 가시 동작 없음. REST 컨트롤러·부트스트랩(`@SpringBootApplication`)이 아직 없어 서비스로 부팅되지 않는다
  (지금 단계 다른 도메인 모듈과 동일한 상태 — 의도된 것).
- 내부적으로는 `List<AptTransaction>` → 해제 제외 → 중위 거래금액/중위 ㎡당 단가 집계(`MarketStat`)까지
  결정적으로 계산 가능하다.

## 본 턴에서 구현하지 않은 T3 체크리스트(명시적 범위 밖)
- `MarketStatService` — `transaction-service`의 `GET /api/v1/transactions`를 WebClient(`lb://transaction-service`)로
  호출해 거래를 가져오는 애플리케이션 서비스(HTTP 조회 클라이언트). 이번 턴 요청 아님.
- `AnalyticsController` — `GET /api/v1/market-stats`(`05_api §4`) REST 레이어. 이번 턴 요청 아님.
- `AnalyticsApplication` — `@SpringBootApplication` 부트스트랩. 이번 턴 요청 아님(그래서 모듈이 아직 부팅되지 않음).
- 산출 트리거 설계(즉시 재산출 vs 조회 시점 캐시 미스 산출) 미결정.
- `MarketStat` 지속화 저장소(store/repository) 및 `sourceTransactionCount`/`computedAt` 등 저장 메타 미구현.
- PER-001(응답 P99 300ms)·PER-003(원장 쓰기/통계 조회 부하 격리) 확인용 벤치마크/부하테스트 미실시.

## 검증한 회귀 범위
- 직접: `analytics-service` — `./gradlew :analytics-service:test` BUILD SUCCESSFUL(3 테스트 green).
  - `MarketStatCalculatorTest.medianOfOddCount`: 700M/900M/800M(전건 비해제) → `tradeCount=3`,
    `medianPriceWon=800M`(정렬 [700,800,900]의 가운데).
  - `MarketStatCalculatorTest.excludesCanceledDeals`: 700M/800M(비해제)+5,000M(해제) → 해제 제외로
    `tradeCount=2`, `medianPriceWon=750M`((700M+800M)/2). 해제 이상치(5,000M)가 통계에 미반영됨을 확인.
  - `MarketStatCalculatorTest.emptyWhenNoTrades`: 빈 목록 → `tradeCount=0`, `medianPriceWon=0L`
    (`MarketStat.empty(...)`).
- 구조 게이트: `python3 sdd/99_toolchain/01_automation/run_arch_check.py` → **7/7 PASS**(exit 0).
  이번 슬라이스로 `analytics-service → common 의존 : import 확인` 규칙이 FAIL→PASS로 전환됐다
  (메인 소스가 `kr.elice.realfield.common.AptTransaction`을 import). "analytics→transaction 조회
  (CQRS read 분리) : lb://transaction-service" 규칙은 설정 레벨 점검이라 이번 도메인 슬라이스와 무관하게 통과.
- 하류(계약만, 미검증): `transaction-service GET /api/v1/transactions` 조회 계약은 조회 클라이언트 구현
  시점에 통합 재확인 대상.
- 오케스트레이션 세션 독립 재검증(T2/T3/T4 병렬 트랙 완료 후, 전체 리포지토리 기준): `./gradlew test`
  전 모듈 BUILD SUCCESSFUL, `run_arch_check.py` 7/7 PASS 재확인. `common.AptTransaction`은 이 슬라이스가
  소비하는 시점에 이미 최종 형태(`pricePerSquareMeter()` 포함, `buildYear` primitive)였다.

# T1 · 수집(ingestion) + 공유 계약 슬라이스 · 구현 요약 (03_build)

> SDD 'build' 산출물. current-state only — dated execution narrative 금지.
> 대상 위치: `sdd/03_build/01_feature/02_t1_ingestion.md`

## 구현 범위
- 구현한 기능/경계:
  - `common` 정합 계약: `DealAmountParser`(DAR-002 금액 정규화 단일 강제 지점), `AptTransaction`(표준 거래 DTO).
  - `ingestion-service` 수집 경계: MOLIT 상세(Dev) 엔드포인트 단일 페이지 호출(`MolitApiClient`)과
    원천 item → 표준 스키마 정규화(`AptTransactionNormalizer`).
  - 외부 장애 격리: `@Retry(name="molitApi")` + `@CircuitBreaker(name="molitApi", fallback)` 로
    재시도 소진·서킷 오픈을 fetch 경계 안에 가둔다(AC-2). fallback은 예외/‌null 대신 실패 결과 객체 반환.
  - serviceKey·전체 URL 로그/예외 비노출(SEC-003): 로그에 path·파라미터만 남기고 serviceKey는 `***` 마스킹,
    실패 로그는 예외 클래스명만 기록.

## 변경 모듈
- common:
  - `kr.elice.realfield.common.DealAmountParser` — `toWon(String):long`. 공백·콤마 제거 → 만원 → ×10000.
    null·공백·비숫자·0 이하 결과는 `IllegalArgumentException`(품질 게이트 신호, 조용한 0 대체 금지).
  - `kr.elice.realfield.common.AptTransaction` — 정규화된 거래 1건의 표준 record. **11필드**
    (`sggCd, umdNm, aptNm, exclusiveArea, floor, buildYear, dealYear, dealMonth, dealDay, dealAmountWon,
    canceled`) + `naturalKey()`. 필드 구성은 `04_data` §1.1(자체 계획 문서)이 아니라 이 저장소에 이미
    커밋되어 있던 `transaction-service/IdempotentUpsertTest`·`analytics-service/MarketStatCalculatorTest`가
    고정한 계약을 정본으로 따랐다 — 자세한 경위는 아래 "명명·형태 정합 메모" 참조.
  - `build.gradle` 변경 없음(java.time 외 신규 의존 불필요).
- ingestion-service:
  - `kr.elice.realfield.ingestion.client.MolitAptTradeItem` — 원천 XML item(문자열 14필드) record.
  - `kr.elice.realfield.ingestion.client.MolitAptTradeResponse` — header/body/items.item[]/페이징 메타 XML DTO.
  - `kr.elice.realfield.ingestion.client.MolitFetchResult` — 페이지 수집 성공/실패 래퍼.
  - `kr.elice.realfield.ingestion.client.MolitApiClient` — WebClient(block) 단일 페이지 호출 + resilience4j.
  - `kr.elice.realfield.ingestion.domain.AptTransactionNormalizer` — item → `AptTransaction`,
    금액은 `common.DealAmountParser`에 위임(콤마/×10000 재구현 없음), `cdealType=="O"` → `canceled=true`.
  - `application.yml` 드리프트 정정(아래 참조).
- api-gateway / config-server / service-discovery: 변경 없음(config-server의 `ingestion-service.yml`은 T4 소유이므로 미변경).

## 계약·자산
- 데이터 계약(스키마·정합):
  - `AptTransaction`(최종): `sggCd, umdNm, aptNm, exclusiveArea, floor, buildYear(nullable), dealYear,
    dealMonth, dealDay, dealAmountWon, canceled` + `naturalKey()`. `04_data` §1.1의 전체 필드 표
    (umdCd·jibun·aptSeq·aptDong·dealingGbn·estateAgentSggNm·slerGbn·buyerGbn·landLeaseholdGbn·rgstDate·
    canceledDate)보다 **좁다** — 이 저장소의 pin된 테스트 계약이 그 범위만 요구했고, 저장 시점
    파생(pricePerArea)·시스템(collectedAt)은 애초에 적재 경계(T2) 책임이라 제외했다. 이 축소는 알려진
    계획-구현 드리프트다: `01_planning/04_data/realprice_data.md` §1.1을 갱신하거나, 이 좁은 계약을
    의도적 최소 슬라이스로 재승인할지는 사용자 판단이 필요하다(둘 다 아직 하지 않음).
  - 정합 규칙 소유: 금액 만원→원(DAR-002)은 `DealAmountParser` 한곳에서만 강제. 해제 판정
    (`cdealType=="O"`)은 정규화기 내부의 단순 조건식으로 처리(공유 클래스 요청 없었음, 04_data가 원하던
    `cdealDay`/해제사유발생일 보관은 `AptTransaction`에 저장할 필드가 없어 현재 버려진다 — 위와 동일한 드리프트).
- 명명·형태 정합 메모: 이 슬라이스는 리포지토리에 이미 커밋되어 있던 4개 pin 테스트
  (`common/DealAmountParserTest`, `ingestion-service/AptTransactionNormalizerTest`,
  `transaction-service/IdempotentUpsertTest`, `analytics-service/MarketStatCalculatorTest` — 전부 T1
  착수 이전부터 존재)가 고정한 계약명·시그니처를 따른다. 최초 구현 시도는 `common/DealAmountParserTest`·
  `ingestion-service/AptTransactionNormalizerTest`만 확인하고 `AptTransaction`을 14필드(jibun·dealingGbn·
  canceledDate 포함)로 만들어 `./gradlew :common:test :ingestion-service:test`는 통과했지만,
  `transaction-service`·`analytics-service`의 pin 테스트가 기대하는 11필드 생성자와 어긋나
  `compileTestJava`가 깨졌다(두 모듈 모두 아직 메인 소스가 없어 이전에는 드러나지 않던 문제).
  오케스트레이션 세션에서 `AptTransaction`을 11필드로 재작성하고 `AptTransactionNormalizer`가 그 형태로만
  매핑하도록 수정해 재검증했다 — 계획서의 `DealAmountNormalizer`(구명)·`AptTransactionDto`/`.dto`·
  `.normalize` 표기는 상위 근사치였고, 실제로는 이 4개 pin 테스트가 유일한 정본이었다.
- 드리프트 정정(1건, 엔드포인트): `ingestion-service/src/main/resources/application.yml`의
  `molit.apt-trade-path`를 기본(비-Dev) `/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade` → 상세(Dev)
  `/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev`로 정정(`07_integration` §1). config-server
  복사본은 T4 소관이라 미변경.

## 현재 사용자 가시 동작
- 수동/자동 수집 트리거(`POST /api/v1/ingest/jobs`) 및 페이징·적재 파이프라인은 아직 없어 외부 가시 동작은 없다.
- 내부적으로 MOLIT 단일 페이지 호출 → XML 파싱 → 표준 거래 정규화 → 금액/해제 정합까지 조립 가능하다.

## 본 턴에서 구현하지 않은 T1 체크리스트(명시적 범위 밖)
- `totalCount` 기준 전량 페이징 루프.
- resultCode 매트릭스(`07_integration` §3) 분기 처리(현재는 fetch 성공/실패 래핑까지만).
- `POST /api/v1/ingest/jobs` REST 컨트롤러(`05_api` §2 응답 스키마).
- transaction-service `POST /internal/transactions/batch-upsert` HTTP 클라이언트 호출.
- 시군구 단위 동시성 제한(세마포어 5) 및 트래픽 초과(22) 백오프·이월(`07_integration` §5).
- `MolitDateParser`(YY.MM.DD 파싱)·`CancelStatusResolver`(별도 클래스) 등 계획서(`01_common_contract.md`)가
  원래 그렸던 나머지 common 계약은 만들지 않았다. 자연키는 별도 `AptTransactionNaturalKey` 클래스 대신
  `AptTransaction.naturalKey()` 인스턴스 메서드로 최소 구현했다(`04_data` §1.2, 9필드 조합).

## 검증한 회귀 범위
- 직접: `common`, `ingestion-service` — `./gradlew :common:test :ingestion-service:test` BUILD SUCCESSFUL.
  - `DealAmountParserTest`: 정상·선행공백없음·복수콤마·빈값/공백/null·비숫자·0/음수.
  - `AptTransactionNormalizerTest`: 정상 매핑·`cdealType=O` 해제 표시·금액 파싱불가 스킵신호·면적 0이하 스킵신호.
- 공유(common 형태 변경의 하류 영향, AptTransaction 재작성 후 명시적으로 재확인):
  - `./gradlew :transaction-service:compileTestJava :analytics-service:compileTestJava` — 여전히
    FAILED이지만, 에러가 `AptTransaction` 생성자 불일치에서 `TransactionCommandService`/`AptTradeStore`/
    `MarketStat`/`MarketStatCalculator` 심볼 없음으로 바뀐 것을 확인했다. 즉 두 모듈은 T2/T3 자체 미구현
    때문에 실패하는 것이지, 본 턴에서 확정한 `AptTransaction` 형태 때문이 아니다(회귀 없음).
- 구조 게이트: `python3 sdd/99_toolchain/01_automation/run_arch_check.py` → `5/7 PASS`. PASS: 필수 7모듈,
  common 역의존 없음, ingestion-service→common 의존, 게이트웨이 3라우트, analytics→transaction CQRS 조회.
  FAIL 2건(`transaction-service`·`analytics-service` → common 의존)은 두 모듈에 아직 메인 소스가
  전혀 없어서다 — T2/T3 트랙에서 해소.
- 하류(계약만, 미검증): transaction-service batch-upsert 계약(`05_api` §3b) — T2 구현 완료 후 통합 재확인 대상.

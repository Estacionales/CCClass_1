# Feature: RealField 실거래 수집·정합·조회 (realprice_ingest)

> SDD 1단계(01_planning) 정본. `00_sources/02_requirements/realfield-부동산실거래.md` §9의 원문 요구(1~5)를
> 검증 가능한 EARS(Easy Approach to Requirements Syntax) 수용기준(AC-1~AC-5)으로 정제한다.
> 원천: `00_sources/02_requirements/realfield-부동산실거래.md`(SFR/DAR/SIR/PER/SECR/CONR),
> `00_sources/01_apis/molit_apt_trade_api.md`(API 계약), `00_sources/03_data_spec/realprice_data_spec.md`(데이터 명세).

---

## 1. 기능 개요

RealField는 국토교통부 아파트 매매 실거래가 OpenAPI를 시군구(LAWD_CD) × 계약월(DEAL_YMD) 단위로 수집하여
표준 스키마(AptTransaction)로 정규화·멱등 적재하고, 해제(취소) 거래를 제외한 시세 통계를
거래원장과 분리된 조회 모델(MarketStat)에서 제공한다.

- 수집: `ingestion-service` (T1)
- 거래원장 write model: `transaction-service` (T2)
- 시세 통계 read model: `analytics-service` (T3), CQRS
- 공유 계약(자연키, 금액 파서 등): `common`

## 2. EARS 수용기준

### AC-1 — 시군구·계약월 단위 수집·표준 적재

> 원문 요구 1. 시군구·계약월 단위 수집·표준 적재. 관련: SFR-001~003, SFR-005, DAR-001.

- WHEN 수집 서비스가 시군구코드(LAWD_CD, 5자리)와 계약년월(DEAL_YMD, YYYYMM)을 입력받으면,
  수집 서비스는 `getRTMSDataSvcAptTradeDev` 상세 엔드포인트를 호출한다. [SFR-001, SIR-001]
- WHILE 응답의 `totalCount`가 지금까지 수집한 `numOfRows × pageNo`보다 크면,
  수집 서비스는 다음 페이지를 계속 호출하여 전량을 수집한다. [SFR-002]
- WHEN 정상 응답(`resultCode = 000`)의 `item`을 수신하면,
  수집 서비스는 각 필드를 표준 거래 스키마(AptTransaction)로 매핑한다. 매핑 규칙은
  `03_data_spec/realprice_data_spec.md` §6 사상 요약을 정본으로 한다. [SFR-003, DAR-001]
- IF `resultCode`가 `000`이 아니면, THEN 수집 서비스는 해당 응답의 `item`을 적재하지 않는다.
  (03 NODATA는 정상 종료로, 01/04/99는 재시도로, 20/30/31/32는 즉시 실패로 분기한다.) [데이터 품질 게이트]
- WHEN 정규화된 거래를 적재하면, 거래원장은 자연키 기반 upsert로 저장한다. [SFR-005, DAR-003]

### AC-2 — 외부 지연·실패에도 무중단(회복력)

> 원문 요구 2. 외부 지연·실패에도 무중단. 관련: SFR-011, SIR-005, PER-003.

- IF 외부 API 호출이 타임아웃되거나 재시도 대상 에러코드(01 APPLICATION ERROR, 04 HTTP ERROR, 99 UNKNOWN)를
  반환하면, THEN 수집 서비스는 resilience4j 재시도·서킷브레이커 정책에 따라 재호출한다. [SIR-005]
- IF 트래픽 초과(22 LIMITED NUMBER OF SERVICE REQUESTS EXCEEDS)가 발생하면,
  THEN 수집 서비스는 백오프 후 재시도하거나 익일로 수집을 이월한다. [SIR-005, CONR-001]
- IF 일부 시군구 또는 일부 페이지의 수집이 실패하면,
  THEN 배치는 실패 구간을 건너뛰고 성공한 구간의 적재와 나머지 구간의 수집을 계속 진행한다. [SFR-011]
- WHILE 수집 배치가 실행 중이어도, 시세 통계 조회(AC-5)의 응답 시간은 열화되지 않는다.
  CQRS로 조회 경로와 수집 경로를 격리하여 보장한다. [PER-003]

### AC-3 — 거래금액 콤마 정규화 및 해제거래 집계 제외 (정합)

> 원문 요구 3. 거래금액 콤마 문자열 변환과 해제거래 집계 제외. 관련: SFR-004, SFR-006, DAR-002, DAR-004, DAR-005.

- WHEN `dealAmount` 문자열(만원 단위, 천 단위 콤마·선행 공백 포함)을 수신하면,
  수집 서비스는 공백과 콤마를 제거해 만원 정수를 얻고 10,000을 곱해 원 단위 정수(`dealAmountWon`)로
  변환한다. 예: `"  82,500"` → `825,000,000`(원). [SFR-004, DAR-002]
- IF 콤마·공백 제거 후 숫자로 파싱할 수 없거나 변환 결과가 0 이하이면,
  THEN 해당 거래는 적재를 스킵하고 부분 수집 실패 건으로 보고한다. [데이터 품질 게이트, SFR-011]
- WHEN `cdealType`이 `O`(해제)이면, 수집 서비스는 해당 거래를 `canceled = true`로 저장하고
  해제사유발생일(`cdealDay`, `YY.MM.DD` → 4자리 연도 날짜, 공백은 null)을 함께 보관한다.
  `cdealType`이 공백이면 `canceled = false`로 저장한다. [SFR-006, DAR-004]
- WHERE 거래가 `canceled = true`인 경우, 시세 통계 read model(MarketStat)은 집계(중위 거래금액·
  중위 ㎡당 단가·집계 거래 수) 산출 시 해당 거래를 제외한다. 거래원장에는 삭제하지 않고 그대로
  보존한다(논리적 제외, 이력 보존). [SFR-006, SFR-008, DAR-005]
- IF 재수집으로 `cdealType`이 정상에서 해제로 전환되면,
  THEN 시스템은 동일 자연키 upsert로 `canceled` 상태 전환을 반영한다. [CONR-005, SFR-013]

### AC-4 — 재수집 멱등성 (중복 0)

> 원문 요구 4. 같은 구간 재수집에도 중복 0. 관련: SFR-005, SFR-013, DAR-003.

- WHEN 동일 자연키(자연키 정의는 `01_planning/04_data` 정본)의 거래가 재수집되면,
  거래원장은 신규 행을 추가하지 않고 기존 행을 갱신한다(upsert). [SFR-005, DAR-003]
- WHEN 과거 계약월 구간을 백필 재수집하면,
  시스템은 신규 수집과 동일한 멱등성을 보장하며 적재 건수만 변동하고 중복 행은 생기지 않는다. [SFR-013]

### AC-5 — 시세 통계는 분리된 조회 모델(CQRS)

> 원문 요구 5. 시세 통계는 거래원장과 분리된 조회 모델에서 신속 제공. 관련: SFR-008, SFR-009, DAR-007, PER-003.

- WHEN 거래 조회 API가 시군구·계약 연월 조건으로 호출되면,
  시스템은 거래원장(write model, transaction-service)에서 표준 거래 목록을 반환한다. [SFR-007]
- WHEN 시세 통계 조회 API가 시군구·계약 연월 조건으로 호출되면,
  시스템은 분석 read model(MarketStat, analytics-service)에서 집계 거래 수·중위 거래금액·
  중위 ㎡당 단가를 반환하며, `canceled = true` 거래는 집계에서 제외한다(AC-3와 정합). [SFR-008, SFR-009, DAR-007]
- 시세 통계 조회의 응답시간은 P99 300ms 이내를 목표로 한다(세부 목표·측정 방법은
  `08_nonfunctional/realprice_nonfunctional.md` 정본). [PER-001]

## 3. 요구사항 추적표

| AC | 원문 요구 | 관련 SFR/DAR/SIR/PER |
| --- | --- | --- |
| AC-1 | 시군구·계약월 단위 수집·표준 적재 | SFR-001, SFR-002, SFR-003, SFR-005, DAR-001, SIR-001 |
| AC-2 | 외부 지연·실패에도 무중단(회복력) | SFR-011, SIR-005, PER-003, CONR-001 |
| AC-3 | 금액 정규화·해제거래 제외(정합) | SFR-004, SFR-006, DAR-002, DAR-004, DAR-005, CONR-005 |
| AC-4 | 재수집 중복 0(멱등) | SFR-005, SFR-013, DAR-003 |
| AC-5 | 통계는 분리된 조회 모델(CQRS) | SFR-007, SFR-008, SFR-009, DAR-007, PER-001, PER-003 |

## 4. 범위 밖 / 후속 정본 참조

- MSA 경계 결정과 기각한 대안: `01_planning/03_architecture/realprice_architecture.md`.
- 자연키 상세 구성, AptTransaction 필드·타입 매핑 전체 표: `01_planning/04_data/realprice_data.md`.
- 거래 조회·시세 통계 조회 API 계약: `01_planning/05_api/realprice_api.md`.
- 외부 연계 회복력 정책 값(재시도 횟수·서킷 임계치·엔드포인트 확정): `01_planning/07_integration/molit_integration.md`.
- 비기능 수용기준(성능·가용성): `01_planning/08_nonfunctional/realprice_nonfunctional.md`.
- 보안 수용기준: `01_planning/09_security/realprice_security.md`.

## 5. 구현 정합 참고 (드리프트)

- `config-server/src/main/resources/config/ingestion-service.yml`의 `molit.apt-trade-path`가 현재
  기본(non-Dev) 엔드포인트(`/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade`)를 가리킨다. 본 문서 AC-1은
  상세(Dev) 엔드포인트(`/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev`)를 표준으로 채택하므로
  (SIR-001, `00_sources/01_apis/molit_apt_trade_api.md` §2), 수집 구현 시 이 설정을 상세 엔드포인트로
  정정해야 한다. 엔드포인트 확정 근거와 정정 지시의 정본은
  `01_planning/07_integration/molit_integration.md` §1이다. 아직 코드 구현 전이므로 본 절에는
  드리프트 요약만 남긴다.

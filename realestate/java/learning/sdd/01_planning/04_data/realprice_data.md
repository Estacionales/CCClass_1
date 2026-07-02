# Data: RealField 표준 거래·통계 데이터 모델 (realprice_data)

> SDD 1단계(01_planning) 정본. `00_sources/03_data_spec/realprice_data_spec.md`(원천 항목·코드 도메인)와
> `00_sources/02_requirements/realfield-부동산실거래.md`의 DAR를 내부 표준 스키마로 사상(map)한다.
> DAR-001(표준 스키마)·DAR-003(자연키)의 정본이 본 문서다. 경계는 `03_architecture/realprice_architecture.md`
> (D-1, D-2, D-4)를 따른다: `AptTransaction`은 `transaction-service`(write model), `MarketStat`은
> `analytics-service`(read model), 매핑·정규화 규칙은 `common`(공유 계약).

---

## 1. AptTransaction — 표준 거래 스키마 (write model, transaction-service)

### 1.1 필드 사상 (원천 → 내부 표준)

> 원천 타입은 전량 XML 문자열(CONR-002). 비고의 "필수"는 데이터 품질 게이트(데이터명세서 §5) 기준 상시 존재가
> 보장되는 항목, "선택"은 결측을 허용하는 항목이다.

| 내부 필드 | 타입 | 원천 필드 | 변환 규칙 | 필수 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `sggCd` | `String(5)` | `sggCd` | 동일(trim) | 필수 | DAR-001 |
| `umdNm` | `String` | `umdNm` | trim | 필수 | DAR-001 |
| `umdCd` | `String(5)` | `umdCd` | trim | 선택 | 데이터명세서 §1.1 |
| `jibun` | `String` | `jibun` | trim | 선택 | 데이터명세서 §1.1 |
| `aptNm` | `String` | `aptNm` | trim | 필수 | DAR-001 |
| `aptSeq` | `String` | `aptSeq` | trim, 형식 `시군구코드-단지번호` | 선택 | 데이터명세서 §1.2 |
| `aptDong` | `String` | `aptDong` | trim, 결측 허용(등기 미완료 시 공백) | 선택 | CONR-004 |
| `exclusiveArea` | `double` | `excluUseAr` | 문자열 → double, 단위 ㎡ | 필수 | DAR-006 |
| `floor` | `int` | `floor` | 문자열 → int | 필수 | DAR-006 |
| `buildYear` | `Integer` | `buildYear` | 문자열 → int, 결측 허용 | 선택 | DAR-006 |
| `dealYear` | `int` | `dealYear` | 문자열 → int | 필수 | DAR-006 |
| `dealMonth` | `int` | `dealMonth` | 문자열 → int | 필수 | DAR-006 |
| `dealDay` | `int` | `dealDay` | 문자열 → int | 필수 | DAR-006 |
| `dealAmountWon` | `long` | `dealAmount` | 공백·콤마 제거 → 만원 정수 → ×10000 | 필수 | DAR-002, AC-3 |
| `dealingGbn` | `String` | `dealingGbn` | trim, 결측 허용 | 선택 | 데이터명세서 §2.1 |
| `estateAgentSggNm` | `String` | `estateAgentSggNm` | trim, 결측 허용 | 선택 | 데이터명세서 §1.3 |
| `slerGbn` | `String` | `slerGbn` | trim, 결측 허용, 원천 범주값 그대로 보존 | 선택 | SECR-004, 데이터명세서 §2.2 |
| `buyerGbn` | `String` | `buyerGbn` | trim, 결측 허용, 원천 범주값 그대로 보존 | 선택 | SECR-004, 데이터명세서 §2.2 |
| `landLeaseholdGbn` | `String` | `landLeaseholdGbn` | trim(`Y`/`N`), 결측 허용 | 선택 | 데이터명세서 §2.3 |
| `rgstDate` | `LocalDate` | `rgstDate` | `YY.MM.DD` → `LocalDate`, 공백은 null | 선택 | CONR-004, 데이터명세서 §3.2 |
| `canceled` | `boolean` | `cdealType` | `== "O"` → `true`, 공백 → `false` | 필수(파생) | DAR-004, AC-3 |
| `canceledDate` | `LocalDate` | `cdealDay` | `YY.MM.DD` → `LocalDate`, 공백은 null | 선택 | DAR-004, CONR-005 |
| `pricePerArea` | `long` | (파생) | `dealAmountWon / exclusiveArea` (원/㎡), 저장 시점 계산 | 필수(파생) | 데이터명세서 §3.3 |
| `collectedAt` | `Instant` | (시스템) | 적재 시각(감사·재수집 추적용) | 필수(시스템) | SFR-013 추적 |

> 미채택 원천 항목(`landCd`, `bonbun`, `bubun`, `roadNm*`)은 표준 스키마에 포함하지 않는다. 자연키·집계·조회
> 어느 요구사항(SFR/DAR)에도 쓰이지 않는 주소 부속 코드이며, 필요 시 후속 확장 항목으로 추가한다(YAGNI).

### 1.2 자연키 설계 (DAR-003)

**결정**: 자연키는 데이터 품질 게이트(데이터명세서 §5)가 상시 보장하는 필수 항목만으로 구성한다.

```text
NaturalKey = (sggCd, umdNm, aptNm, exclusiveArea, floor, dealYear, dealMonth, dealDay, dealAmountWon)
```

- DB 유니크 제약: 위 9개 컬럼의 복합 유니크 인덱스.
- `aptSeq`를 자연키에 넣지 않는 이유: `aptSeq`는 선택 항목(데이터명세서 §1.2)이라 공백일 수 있고, 공백을 자연키에
  포함하면 서로 다른 단지의 결측 레코드가 동일 키로 충돌한다. `aptSeq`가 있는 경우에도 `aptNm`+`umdNm`이 이미
  단지를 사실상 특정하므로 중복 판별력에 크게 기여하지 않는다.
- `jibun`을 자연키에 넣지 않는 이유: 표시용 지번 문자열은 선택 항목이며 표기 변형(선행 0, 구분자)이 있어 정규화
  비용 대비 판별력이 낮다.
- 알려진 트레이드오프: 동일 단지·동일 면적·동일 층에서 같은 날 같은 금액으로 체결된 서로 다른 두 건이 이론상
  존재할 수 있다(예: 같은 라인 다른 호수). 이 경우 두 번째 건이 첫 번째 건에 upsert되어 손실될 수 있다. 원천이
  호수(동/호) 식별자를 공개하지 않으므로(SECR-004, 개인정보 보호 목적) 시스템이 구조적으로 구분할 수 없다.
  이 한계는 알려진 제약으로 문서화하며, 집계(중위값) 성격상 실사용 영향은 낮다고 판단한다.

**기각한 대안**:
- **원천이 제공하는 고유 ID를 자연키로 사용**: 원천 API(§4.3, `00_sources/01_apis/molit_apt_trade_api.md`)는
  거래 단위 고유 ID를 제공하지 않는다. 채택 불가.
- **`aptSeq`를 필수로 포함하고 결측 시 별도 fallback 키 사용(이중 키 전략)**: 유니크 제약이 컬럼 조합에 따라
  분기되어 DB 제약으로 표현하기 어렵고(부분 유니크 인덱스 필요), 구현 복잡도 대비 판별력 향상이 작아 기각.
- **synthetic UUID + 재수집 시 항상 신규 insert(멱등성 없음)**: DAR-003·AC-4(재수집 중복 0)를 정면 위반. 기각.
- **`jibun`까지 포함해 판별력 강화**: 표기 변형으로 인해 오히려 동일 거래가 다른 키로 갈라져 중복 행을 만들
  위험(false negative dedup)이 있어 기각. 필수 항목만으로 구성된 현재 키가 더 안정적이다.

### 1.3 해제(canceled) 처리와 이력 보존 (DAR-004, DAR-005)

- `canceled=true`row는 삭제하지 않는다. 재수집으로 `cdealType`이 정상→해제로 바뀌면 자연키 upsert가 같은 행의
  `canceled`/`canceledDate`를 갱신한다(CONR-005).
- `transaction-service`의 조회 API(SFR-007)는 `canceled` 값과 무관하게 원장 전체를 반환한다. 집계 제외는
  `analytics-service`(read model) 책임이다(§2).

## 2. MarketStat — 시세 통계 read model (analytics-service)

### 2.1 스키마

| 필드 | 타입 | 설명 | 근거 |
| --- | --- | --- | --- |
| `sggCd` | `String(5)` | 시군구 법정동코드 | SFR-008 |
| `dealYearMonth` | `String(6)` (`YYYYMM`) | 계약 연월. 조회 조건과 동일 형식(DEAL_YMD) | SFR-008 |
| `transactionCount` | `long` | `canceled=false`인 거래 건수 | SFR-008, DAR-007 |
| `medianDealAmountWon` | `long` | `canceled=false` 거래의 `dealAmountWon` 중위값 | DAR-007 |
| `medianPricePerArea` | `long` | `canceled=false` 거래의 `pricePerArea`(원/㎡) 중위값 | DAR-007, 데이터명세서 §3.3 |
| `sourceTransactionCount` | `long` | 집계 대상(canceled 포함 전체) 원장 건수, 참고용 | 운영 가시성(해제 비율 모니터링) |
| `computedAt` | `Instant` | 통계 산출(갱신) 시각 | D-3 REST 동기 조회 특성상 최신성 확인용 |

- 집계 키: `(sggCd, dealYearMonth)`. SFR-008 조회 조건(시군구·계약 연월)과 1:1 대응한다.
- 중위값 계산: `canceled=false` 거래를 `dealAmountWon`(또는 `pricePerArea`) 기준 정렬 후, 건수가 홀수면 중앙값,
  짝수면 중앙 두 값의 평균(정수 반올림)을 취한다.
- `sourceTransactionCount - transactionCount`가 해당 시군구·연월의 해제 거래 수다(파생 지표, 별도 저장하지 않음).

### 2.2 산출 경로

`analytics-service`는 `transaction-service`의 조회 API(§5 `GET /api/v1/transactions`)를 `sggCd`+`dealYm` 조건으로
호출해 원장을 읽고, 애플리케이션 레벨에서 `canceled=false` 필터링과 중위값 연산을 수행한 뒤 `MarketStat`을
저장/캐시한다(경계 근거는 `03_architecture` D-2/D-3).

## 3. 마스터 데이터 — LAWD_CD (DAR-008)

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `lawdCd` | `String(5)` | 시군구 법정동코드(요청 파라미터 `LAWD_CD`) |
| `sidoNm` | `String` | 시도명 |
| `sggNm` | `String` | 시군구명 |

- 출처: 행정표준코드관리시스템(SIR-006). 250개 시군구 전체를 마스터로 보관한다.
- 소유: `common`(공유 참조 데이터) 또는 `ingestion-service`(수집 스케줄 구동용). 변경 빈도가 낮고 도메인 서비스
  전체가 참조하므로 `common`에 정적 리소스(예: `lawd_codes.csv`)로 두는 편을 기본으로 하되, 확정은
  `02_plan/01_feature` 구현 계획에서 결정한다(본 문서는 데이터 계약만 정의).

## 4. 공유 계약 — common 모듈 책임 (D-4)

| 계약 | 역할 | 근거 |
| --- | --- | --- |
| `AptTransactionDto` | 서비스 간 전송용 표준 거래 DTO(§1.1 필드) | DAR-001, 구조 게이트 규칙 3 |
| `DealAmountNormalizer` | `dealAmount` 문자열 → `dealAmountWon` 원 단위 변환(공백·콤마 제거, ×10000) | DAR-002, AC-3 |
| `CancelStatusResolver` | `cdealType` → `canceled` boolean 판정 | DAR-004, AC-3 |
| `MolitDateParser` | `YY.MM.DD` → `LocalDate`(공백은 null) | 데이터명세서 §3.2 |
| `AptTransactionNaturalKey` | §1.2 자연키 9개 필드 조합·동등성 판정 | DAR-003, AC-4 |

패키지 컨벤션: `kr.elice.realfield.common.*`(구조 게이트가 `kr.elice.realfield.<domain>` 임포트 존재로 도메인
의존을 검증하므로, 도메인 모듈은 `kr.elice.realfield.common` import로 이 계약을 소비한다).

## 5. 요구사항 추적표

| 데이터 요소 | 관련 DAR | 관련 AC |
| --- | --- | --- |
| AptTransaction 필드 사상(§1.1) | DAR-001, DAR-006 | AC-1 |
| 금액 정규화(§1.1 `dealAmountWon`) | DAR-002 | AC-3 |
| 자연키(§1.2) | DAR-003 | AC-1, AC-4 |
| 해제 플래그·이력 보존(§1.3) | DAR-004, DAR-005 | AC-3 |
| MarketStat 집계(§2) | DAR-007 | AC-5 |
| LAWD_CD 마스터(§3) | DAR-008 | AC-1 |

## 6. 구현 정합 참고 (드리프트)

- `transaction-service/src/main/resources/application.yml`은 현재 `jdbc:h2:mem` + `ddl-auto: create-drop`
  (학습용 인메모리)이다. §1.2 유니크 제약(복합 자연키)은 구현 시 JPA `@Table(uniqueConstraints=...)` 또는
  마이그레이션 스크립트로 명시적으로 걸어야 하며, 아직 코드가 없어 본 절에 계약으로만 기록한다.

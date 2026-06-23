# 데이터 모델 (04_data): 표준 거래 스키마 · 정합 · CQRS read model

> 2단계(아키텍처링) 산출물입니다. 외부 API item을 표준 스키마로 매핑하고, 금액 정규화·자연키·해제 처리·집계 규칙을 정본으로 박제합니다.
> 외부 필드 정의 정본: `00_sources/01_apis/molit_apt_trade_api.md`. 본 문서는 그 원천을 내부 표준으로 사상(map)합니다.
> 추적: DAR-001~DAR-007, AC-1·3·4·5.

---

## 1. 표준 거래 스키마 (AptTransaction)

> 거래원장(write model)의 단일 표준 엔티티입니다. 백엔드가 사용하는 필드명과 정확히 일치합니다.

| 표준 필드 | 타입 | 제약 | 의미 | 원천 필드(data.go.kr) | 변환 |
| --- | --- | --- | --- | --- | --- |
| sggCd | String(5) | NOT NULL | 법정동 시군구코드 | `sggCd` | 그대로 |
| umdNm | String | NOT NULL | 법정동(읍면동)명 | `umdNm` | trim |
| aptNm | String | NOT NULL | 단지명(아파트) | `aptNm` | trim |
| exclusiveArea | double | NOT NULL, > 0 | 전용면적(㎡) | `excluUseAr` | 문자열→double |
| floor | int | NOT NULL | 층 | `floor` | 문자열→int |
| buildYear | int | NULL 허용 | 건축년도 | `buildYear` | 문자열→int |
| dealYear | int | NOT NULL | 계약 연도 | `dealYear` | 문자열→int |
| dealMonth | int | NOT NULL, 1~12 | 계약 월 | `dealMonth` | 문자열→int |
| dealDay | int | NOT NULL, 1~31 | 계약 일 | `dealDay` | 문자열→int |
| dealAmountWon | long | NOT NULL, > 0 | 거래금액(원) | `dealAmount`(만원·콤마) | 콤마/공백 제거 → 만원 정수 → ×10000 |
| canceled | boolean | NOT NULL, default false | 해제 여부 | `cdealType` | `== "O"` → true |

### 1.1 확장 보존 필드 (선택, SFR-012/DAR-005)

원천이 제공하면 손실 없이 보존합니다. 집계에는 쓰지 않으나 원장 추적·감사 목적으로 적재합니다.

| 표준 필드 | 타입 | 의미 | 원천 필드 | 변환 |
| --- | --- | --- | --- | --- |
| jibun | String | 지번 | `jibun` | trim |
| aptDong | String | 아파트 동(등기 완료 건만) | `aptDong` | trim, 공백 허용 |
| aptSeq | String | 단지일련번호 | `aptSeq` | 그대로 |
| dealingGbn | String | 거래유형(중개/직거래) | `dealingGbn` | trim, 공백 허용 |
| estateAgentSggNm | String | 중개사소재지(시군구) | `estateAgentSggNm` | trim |
| slerGbn | String | 매도자 구분 | `slerGbn` | trim |
| buyerGbn | String | 매수자 구분 | `buyerGbn` | trim |
| rgstDate | LocalDate? | 등기일자 | `rgstDate` | `YY.MM.DD`→date, 공백→null |
| canceledDate | LocalDate? | 해제사유발생일 | `cdealDay` | `YY.MM.DD`→date, 공백→null |
| landLeaseholdGbn | String | 토지임대부 여부(Y/N) | `landLeaseholdGbn` | trim |

> 원천 값은 모두 문자열(String)로 내려옵니다(CONR-002). 숫자·날짜는 본 시스템이 형 변환합니다(DAR-006). 등기일자·동은 등기 완료 건만 채워지므로 결측(null)을 허용합니다(CONR-004).

---

## 2. 금액 정규화 규칙 (DAR-002 / AC-3)

원천 `dealAmount`는 만원 단위이며 천 단위 콤마와 선행 공백을 포함합니다.

```
입력:  "  82,500"   (만원, 콤마·공백 포함)
1) 공백 제거:        "82,500"
2) 콤마 제거:        "82500"
3) 만원 정수 파싱:    82500
4) 원 단위 환산(×10000): 825,000,000
저장(dealAmountWon): 825000000  (long)
```

- 변환 책임은 `common` 공유 라이브러리의 금액 파서 1곳에 둡니다(아키텍처 판단 3). 수집·분석이 다르게 구현하면 통계가 어긋나기 때문입니다.
- 파싱 실패(빈 문자열·비정상 토큰)는 적재 거부 사유로 보고하고, 해당 건만 스킵합니다(부분 수집 허용, SFR-011).

---

## 3. 멱등 자연키 (DAR-003 / AC-4)

동일 거래의 재수집을 중복 없이 흡수하기 위한 자연키입니다. 거래원장 테이블에 유니크 제약을 둡니다.

```
naturalKey = sggCd | umdNm | aptNm | exclusiveArea | floor
           | dealYear | dealMonth | dealDay | dealAmountWon
```

- 같은 (시군구·계약월) 구간을 재수집(백필 포함, SFR-013)해도 자연키 충돌 시 upsert로 갱신만 일어나고 중복 행이 생기지 않습니다.
- 자연키에 dealAmountWon을 포함해, 동일 단지·동일 일자에 가격이 다른 별개 거래(다른 호실)를 구분합니다.
- 동(aptDong)은 등기 완료 후에야 채워질 수 있어 결측 변동이 잦으므로 자연키에서 제외합니다. 동을 키에 넣으면 등기 전후로 같은 거래가 두 행이 됩니다.

### 3.1 upsert 동작

| 상황 | 동작 |
| --- | --- |
| 신규 자연키 | INSERT |
| 기존 자연키 + 비키 필드 변동(예: rgstDate 채워짐, canceled 전환) | UPDATE |
| 기존 자연키 + 변동 없음 | no-op(또는 멱등 UPDATE) |

---

## 4. 해제 거래 처리 (DAR-004 / AC-3)

- `cdealType == "O"` 이면 `canceled = true`로 저장하고, `cdealDay`를 `canceledDate`로 보존합니다.
- 해제 거래는 거래원장에는 남기되(DAR-005 이력 보존), 시세 집계(MarketStat)에서는 제외합니다(논리적 제외).
- 재수집 시 원천에서 해제가 사후 표기될 수 있으므로(CONR-005), upsert로 `canceled`를 false→true로 전환합니다. 이 전환은 다음 집계 재산출에 반영됩니다.

---

## 5. 컬럼 타입·제약·예시 (거래원장 DDL 관점)

| 컬럼 | 타입 | 제약 | 예시 |
| --- | --- | --- | --- |
| id | bigint | PK, auto | 1 |
| sgg_cd | varchar(5) | not null | `11110` |
| umd_nm | varchar | not null | `청운동` |
| apt_nm | varchar | not null | `청운현대` |
| exclusive_area | double | not null | `84.97` |
| floor | int | not null | `10` |
| build_year | int | null | `2013` |
| deal_year | int | not null | `2024` |
| deal_month | int | not null | `5` |
| deal_day | int | not null | `23` |
| deal_amount_won | bigint | not null | `825000000` |
| canceled | boolean | not null default false | `false` |
| canceled_date | date | null | `null` |
| rgst_date | date | null | `2024-07-10` |
| dealing_gbn | varchar | null | `중개거래` |
| (자연키 유니크) | unique | sgg_cd, umd_nm, apt_nm, exclusive_area, floor, deal_year, deal_month, deal_day, deal_amount_won |

---

## 6. CQRS read model (MarketStat) 집계 규칙 (DAR-007 / AC-5)

시세 통계는 거래원장과 분리된 분석 read model에서 산출·제공합니다(SFR-009, PER-003).

### 6.1 스키마

| 필드 | 타입 | 의미 |
| --- | --- | --- |
| sggCd | String(5) | 집계 대상 시군구 |
| dealYear | int | 집계 대상 계약 연도 |
| dealMonth | int | 집계 대상 계약 월 |
| tradeCount | int | 집계 대상 거래 수(해제 제외) |
| medianPriceWon | long | 중위 거래금액(원) |
| medianPricePerM2Won | long | 중위 ㎡당 단가(원) |

### 6.2 집계 규칙

```
집계 모집단 = AptTransaction where sggCd, dealYear, dealMonth 일치 AND canceled = false
tradeCount          = 모집단 건수
medianPriceWon      = median(dealAmountWon)
medianPricePerM2Won = median(dealAmountWon / exclusiveArea)   (건별 ㎡단가의 중위값)
```

- 해제(`canceled = true`) 거래는 집계 모집단에서 제외합니다(AC-3).
- ㎡당 단가는 거래별로 `dealAmountWon / exclusiveArea`를 먼저 구한 뒤 그 분포의 중위값을 취합니다(평균이 아닌 중위, 이상치 완화).
- 모집단이 비면(0건) 해당 (시군구·연월)은 통계를 생성하지 않거나 tradeCount=0으로 반환합니다.
- 재수집으로 원장이 갱신되면(신규 적재·해제 전환) 해당 (시군구·연월) 키의 MarketStat를 재산출합니다.

---

## 7. 매핑 요약 (data.go.kr → 내부 표준)

| 원천(data.go.kr) | 내부 표준 | 핵심 변환 |
| --- | --- | --- |
| sggCd | sggCd | 동일 |
| umdNm | umdNm | trim |
| aptNm | aptNm | trim |
| excluUseAr | exclusiveArea | String→double |
| floor | floor | String→int |
| buildYear | buildYear | String→int(결측 허용) |
| dealYear/dealMonth/dealDay | dealYear/dealMonth/dealDay | String→int |
| dealAmount(만원·콤마) | dealAmountWon | 콤마/공백 제거 → 만원 정수 → ×10000 |
| cdealType(`O`) | canceled | `=="O"` → boolean |
| cdealDay | canceledDate | `YY.MM.DD`→date(결측 허용) |
| rgstDate | rgstDate | `YY.MM.DD`→date(결측 허용) |
| dealingGbn/slerGbn/buyerGbn/estateAgentSggNm/aptDong/landLeaseholdGbn | 동명 보존 필드 | trim, 결측 허용 |

> 핵심 변환 4종: (1) 금액 만원→원, (2) 문자열→숫자, (3) 해제 코드→boolean, (4) `YY.MM.DD`→date. 이 네 변환이 정합의 핵심이며 common 라이브러리에서 강제합니다.

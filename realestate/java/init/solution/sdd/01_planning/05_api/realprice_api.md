# API 계약 (05_api): 게이트웨이 라우팅 · 서비스 엔드포인트

> 2단계 산출물입니다. 게이트웨이 단일 진입점 라우팅과 내부 서비스 엔드포인트 계약을 정본으로 정의합니다.
> 추적: SIR-003·SIR-004, SFR-001·007·008, AC-1·5.
> 데이터 스키마 정본: `04_data/realprice_data.md`. 외부 연계 정본: `07_integration/molit_integration.md`.

---

## 1. 게이트웨이 라우팅 테이블

| 경로 패턴 | 대상 서비스 | 메서드 | 설명 |
| --- | --- | --- | --- |
| `/api/v1/ingest/**` | ingestion-service | POST | 외부 수집 트리거 |
| `/api/v1/transactions/**` | transaction-service | GET, POST | 거래원장 적재·조회 |
| `/api/v1/market-stats/**` | analytics-service | GET | 시세 통계 조회(read model) |

- 게이트웨이(Spring Cloud Gateway)가 단일 진입점입니다(SIR-003). 내부 서비스는 직접 외부로 노출하지 않습니다.
- 내부 서비스 간 호출은 디스커버리(Eureka) 로드밸런싱(`lb://`)으로 합니다(SIR-004).
- 공통 응답 규약: 성공 2xx + JSON 본문, 실패 4xx/5xx + 오류 본문(`{"error":{"code","message"}}`).

---

## 2. ingestion-service: 수집 트리거 (SFR-001/010)

### 2.1 단건 수집

```
POST /api/v1/ingest/apt-trade?lawdCd={5자리}&dealYmd={YYYYMM}
```

| 파라미터 | 필수 | 타입 | 설명 | 예시 |
| --- | --- | --- | --- | --- |
| lawdCd | 필수 | String(5) | 법정동 시군구코드 | `11110` |
| dealYmd | 필수 | String(6) | 계약년월 YYYYMM | `202405` |

응답(200):

```json
{ "lawdCd": "11110", "dealYmd": "202405", "fetched": 143, "upserted": 143, "skipped": 0 }
```

| 필드 | 의미 |
| --- | --- |
| fetched | 외부 API에서 받은 거래 수(전 페이지 합) |
| upserted | 멱등 적재된 수(신규+갱신) |
| skipped | 정규화 실패로 스킵된 수(부분 수집, SFR-011) |

상태코드:

| 코드 | 상황 |
| --- | --- |
| 200 | 수집 성공(부분 성공 포함) |
| 400 | lawdCd/dealYmd 형식 오류 |
| 502 | 외부 API 비정상(서킷 open·연속 실패). 부분 수집분은 적재되었을 수 있음 |
| 504 | 외부 API 타임아웃 |

### 2.2 구간 백필(선택, SFR-013)

```
POST /api/v1/ingest/apt-trade/backfill?lawdCd={}&fromYmd={YYYYMM}&toYmd={YYYYMM}
```

응답: 월별 수집 결과 배열. 일부 월 실패해도 성공 월은 적재되고 진행됩니다.

---

## 3. transaction-service: 거래원장 (SFR-005/007)

### 3.1 멱등 적재(내부)

```
POST /api/v1/transactions/bulk
Content-Type: application/json
Body: AptTransaction[]
```

- 자연키 기반 멱등 upsert(AC-4). 중복은 생기지 않습니다.
- 응답(200): `{ "received": 143, "upserted": 143 }` (멱등이므로 재호출 시 중복 증가 없음).
- 주로 ingestion-service가 호출하는 내부 계약입니다.

### 3.2 거래 조회

```
GET /api/v1/transactions?sggCd={}&dealYear={}&dealMonth={}
```

| 파라미터 | 필수 | 타입 | 설명 |
| --- | --- | --- | --- |
| sggCd | 필수 | String(5) | 시군구코드 |
| dealYear | 필수 | int | 계약 연도 |
| dealMonth | 필수 | int | 계약 월 |

응답(200): `AptTransaction[]`

```json
[
  {
    "sggCd": "11110", "umdNm": "청운동", "aptNm": "청운현대",
    "exclusiveArea": 84.97, "floor": 10, "buildYear": 2013,
    "dealYear": 2024, "dealMonth": 5, "dealDay": 23,
    "dealAmountWon": 825000000, "canceled": false
  }
]
```

상태코드: 200(조회 성공, 결과 0건 포함) / 400(파라미터 오류).

---

## 4. analytics-service: 시세 통계 (SFR-008/009)

```
GET /api/v1/market-stats?sggCd={}&dealYear={}&dealMonth={}
```

| 파라미터 | 필수 | 타입 | 설명 |
| --- | --- | --- | --- |
| sggCd | 필수 | String(5) | 시군구코드 |
| dealYear | 필수 | int | 계약 연도 |
| dealMonth | 필수 | int | 계약 월 |

응답(200):

```json
{
  "sggCd": "11110", "dealYear": 2024, "dealMonth": 5,
  "tradeCount": 141, "medianPriceWon": 825000000, "medianPricePerM2Won": 9709309
}
```

| 필드 | 의미 |
| --- | --- |
| tradeCount | 집계 거래 수(해제 제외) |
| medianPriceWon | 중위 거래금액(원) |
| medianPricePerM2Won | 중위 ㎡당 단가(원) |

상태코드:

| 코드 | 상황 |
| --- | --- |
| 200 | 통계 반환(데이터 없으면 tradeCount=0) |
| 400 | 파라미터 오류 |

> 조회는 거래원장(write model)이 아니라 analytics read model(MarketStat)에서 산출합니다(AC-5, SFR-009). 게이트웨이는 단일 진입점이며, analytics-service는 transaction-service 조회 위에 집계 모델을 둡니다.

---

## 5. 공통 오류 규약

```json
{ "error": { "code": "INGEST_UPSTREAM_UNAVAILABLE", "message": "data.go.kr upstream circuit open" } }
```

| code | HTTP | 의미 |
| --- | --- | --- |
| BAD_REQUEST | 400 | 파라미터 형식 오류 |
| INGEST_UPSTREAM_UNAVAILABLE | 502 | 외부 API 비정상/서킷 open |
| INGEST_UPSTREAM_TIMEOUT | 504 | 외부 API 타임아웃 |
| INTERNAL_ERROR | 500 | 내부 오류 |

---

## 6. 계약 무손상 (AC-R)

게이트웨이 라우팅 3종, 디스커버리 등록, 위 조회 API 계약(요청 파라미터·응답 필드)은 회귀로 보호합니다. 변경 시 본 문서를 정본으로 갱신하고 회귀 검증을 통과해야 합니다.

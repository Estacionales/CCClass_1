# API: RealField 내부 REST 계약 (realprice_api)

> SDD 1단계(01_planning) 정본. `03_architecture/realprice_architecture.md`(D-5, 게이트웨이 단일 진입점)와
> `04_data/realprice_data.md`(AptTransaction/MarketStat 스키마)를 API 계약으로 구체화한다.
> 라우팅은 `api-gateway/src/main/resources/application.yml`의 현재 3개 라우트(ingest·transactions·market-stats)를
> 정본 baseline으로 삼는다(SIR-003).

---

## 1. 공통 규약

- 진입점: 모든 외부 호출은 `api-gateway`(port 8080)를 거친다. 도메인 서비스를 직접 호출하지 않는다(SIR-003).
- 인증: 본 사업 범위(요구사항정의서 §2.2)는 대국민 포털 UI를 제외하므로, 이 계약 범위의 엔드포인트는
  내부망 호출을 전제로 하며 최종 사용자 인증(OAuth 등)을 요구하지 않는다. 외부 공개 시 인증 계층 추가는
  별도 후속 과제(§6)로 남긴다.
- 응답 포맷: `application/json`.
- 공통 에러 응답 envelope:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "sggCd는 5자리 숫자여야 합니다.",
  "path": "/api/v1/transactions",
  "timestamp": "2026-07-02T09:00:00Z"
}
```

| HTTP 상태 | code | 의미 |
| --- | --- | --- |
| 400 | `VALIDATION_ERROR` | 요청 파라미터 형식 오류(예: `sggCd` 5자리 아님, `dealYm` `YYYYMM` 아님) |
| 404 | `NOT_FOUND` | 존재하지 않는 리소스(예: 통계 미산출 구간) |
| 502 | `UPSTREAM_UNAVAILABLE` | 외부 API(data.go.kr) 또는 하류 서비스 회복력 정책 소진(서킷 오픈) |
| 500 | `INTERNAL_ERROR` | 처리되지 않은 서버 오류 |

- 페이징 공통 파라미터: `page`(0-base, 기본 0), `size`(기본 20, 최대 200).
- 파라미터 검증 공통 규칙: `sggCd`는 `^[0-9]{5}$`, `dealYm`은 `^[0-9]{6}$`(YYYYMM).

## 2. `POST /api/v1/ingest/jobs` — 수집 트리거 (게이트웨이 라우트: `/api/v1/ingest/**`)

> 근거: SFR-001, SFR-002, SFR-010(수동 트리거), SFR-011(부분 수집), AC-1, AC-2. 소유 서비스: `ingestion-service`.

### 요청

```http
POST /api/v1/ingest/jobs
Content-Type: application/json

{
  "sggCd": "11110",
  "dealYm": "202405"
}
```

| 필드 | 타입 | 필수 | 규칙 |
| --- | --- | --- | --- |
| `sggCd` | string | 필수 | 5자리 숫자(LAWD_CD) |
| `dealYm` | string | 필수 | `YYYYMM` |

### 응답 — `200 OK` (동기 처리, 페이징 전량 수집 완료 후 응답)

```json
{
  "sggCd": "11110",
  "dealYm": "202405",
  "totalCount": 143,
  "pagesFetched": 1,
  "upsertedCount": 140,
  "skippedCount": 3,
  "skippedReasons": [
    { "reason": "INVALID_AMOUNT", "count": 2 },
    { "reason": "MISSING_REQUIRED_FIELD", "count": 1 }
  ]
}
```

| 필드 | 설명 | 근거 |
| --- | --- | --- |
| `totalCount` | 원천 `totalCount`(해당 시군구·연월 전체 신고 건수) | SFR-002 |
| `pagesFetched` | 실제 호출한 페이지 수 | SFR-002 |
| `upsertedCount` | 적재(신규+갱신) 건수 | SFR-005 |
| `skippedCount` / `skippedReasons` | 품질 게이트 위반으로 스킵된 건수·사유(데이터명세서 §5) | SFR-011, AC-3 |

- 부분 실패 처리: 특정 페이지 호출이 회복력 정책 소진(서킷 오픈) 후에도 실패하면, 이미 수집한 페이지는
  적재하고 응답에 `partial: true`와 실패 페이지 목록을 포함한다(AC-2). 배치 전체를 롤백하지 않는다.
- 재수집(백필)도 동일 엔드포인트를 사용한다. 동일 `sggCd`+`dealYm` 재호출은 자연키 upsert로 멱등 처리된다(AC-4).

### 에러

| 상태 | code | 조건 |
| --- | --- | --- |
| 400 | `VALIDATION_ERROR` | `sggCd`/`dealYm` 형식 오류 |
| 502 | `UPSTREAM_UNAVAILABLE` | data.go.kr 서킷 오픈, 트래픽 한도 초과(22) 등 |

## 3. `GET /api/v1/transactions` — 거래 조회 (게이트웨이 라우트: `/api/v1/transactions/**`)

> 근거: SFR-007, AC-5. 소유 서비스: `transaction-service`(write model 조회).

### 요청

```http
GET /api/v1/transactions?sggCd=11110&dealYm=202405&page=0&size=20
```

| 파라미터 | 필수 | 설명 |
| --- | --- | --- |
| `sggCd` | 필수 | 시군구 5자리 |
| `dealYm` | 필수 | 계약 연월 `YYYYMM` |
| `page`, `size` | 선택 | §1 공통 페이징 |

### 응답 — `200 OK`

```json
{
  "content": [
    {
      "sggCd": "11110",
      "umdNm": "청운동",
      "aptNm": "청운현대",
      "aptDong": "101",
      "exclusiveArea": 84.97,
      "floor": 10,
      "buildYear": 2013,
      "dealYear": 2024,
      "dealMonth": 5,
      "dealDay": 23,
      "dealAmountWon": 825000000,
      "pricePerArea": 9709779,
      "dealingGbn": "중개거래",
      "estateAgentSggNm": "서울 종로구",
      "slerGbn": "개인",
      "buyerGbn": "개인",
      "landLeaseholdGbn": "N",
      "rgstDate": "2024-07-10",
      "canceled": false,
      "canceledDate": null
    }
  ],
  "page": 0,
  "size": 20,
  "totalElements": 143
}
```

- 필드는 `04_data/realprice_data.md` §1.1 `AptTransaction` 표준 스키마를 그대로 노출한다.
- `canceled=true` 거래도 포함해 반환한다(원장 이력 보존, DAR-005). 집계 제외는 이 API의 책임이 아니다.
- 정렬: 기본 `dealYear, dealMonth, dealDay DESC`.

### 에러

| 상태 | code | 조건 |
| --- | --- | --- |
| 400 | `VALIDATION_ERROR` | 파라미터 형식 오류 |

## 4. `GET /api/v1/market-stats` — 시세 통계 조회 (게이트웨이 라우트: `/api/v1/market-stats/**`)

> 근거: SFR-008, SFR-009, PER-001, AC-3(해제 제외), AC-5. 소유 서비스: `analytics-service`(read model).

### 요청

```http
GET /api/v1/market-stats?sggCd=11110&dealYm=202405
```

| 파라미터 | 필수 | 설명 |
| --- | --- | --- |
| `sggCd` | 필수 | 시군구 5자리 |
| `dealYm` | 필수 | 계약 연월 `YYYYMM` |

### 응답 — `200 OK`

```json
{
  "sggCd": "11110",
  "dealYm": "202405",
  "transactionCount": 138,
  "medianDealAmountWon": 810000000,
  "medianPricePerArea": 9500000,
  "computedAt": "2026-07-02T09:00:00Z"
}
```

| 필드 | 설명 | 근거 |
| --- | --- | --- |
| `transactionCount` | `canceled=false` 집계 대상 건수 | DAR-007, AC-3 |
| `medianDealAmountWon` | 중위 거래금액(원) | DAR-007 |
| `medianPricePerArea` | 중위 ㎡당 단가(원) | DAR-007 |
| `computedAt` | 통계 산출 시각(D-3 동기 조회 특성상 최신성 확인용) | `04_data` §2.1 |

- 응답 성능 목표: P99 300ms 이내(PER-001). 조회 시 실시간으로 원장 재집계하지 않고, `analytics-service`의
  read model(사전 산출 또는 캐시된 `MarketStat`)에서 조회한다(`04_data` §2.2).

### 에러

| 상태 | code | 조건 |
| --- | --- | --- |
| 400 | `VALIDATION_ERROR` | 파라미터 형식 오류 |
| 404 | `NOT_FOUND` | 해당 시군구·연월에 대해 아직 산출된 통계가 없음(수집 미실행 등) |

## 5. 요구사항 추적표

| 엔드포인트 | 관련 SFR | 관련 AC |
| --- | --- | --- |
| `POST /api/v1/ingest/jobs` | SFR-001, SFR-002, SFR-010, SFR-011 | AC-1, AC-2, AC-4 |
| `GET /api/v1/transactions` | SFR-007 | AC-5 |
| `GET /api/v1/market-stats` | SFR-008, SFR-009 | AC-3, AC-5 |

## 6. 범위 밖 / 후속 과제

- 최종 사용자 인증·인가 계층은 대국민 포털 UI가 범위에 들어올 때 재검토한다(요구사항정의서 §2.2).
- 수집 스케줄링(매월 자동 배치)의 트리거 방식(cron, 스케줄러 서비스)은 본 API 계약에는 포함하지 않으며,
  `POST /api/v1/ingest/jobs`는 수동/스케줄러 공통 진입점으로 설계했다. 배치 오케스트레이션 세부는
  `01_planning/06_iac`(후속 작성 대상)에서 다룬다.

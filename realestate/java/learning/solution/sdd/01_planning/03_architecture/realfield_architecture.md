# RealField 아키텍처 설계 (03_architecture)

> 2단계 '아키텍처링' 산출물입니다. 대규모 MSA이므로 경계·런타임·구조를 명시적으로 남깁니다.
> **이 문서의 결정은 Claude가 자동으로 뱉은 것이 아니라, 서비스 특성을 보고 사람이 판단해 확정한 것입니다.**
> 아래 "사람이 판단한 지점"이 핵심입니다.

## 1. Bounded Context (도메인 경계)

| 컨텍스트 | 책임 | 부하 특성 |
| --- | --- | --- |
| 수집(Ingestion) | data.go.kr 호출·정규화·회복력 | 외부 I/O 바운드, 매월 배치성 |
| 거래원장(Transaction) | 정규화 거래의 멱등 적재·원본 조회 | 쓰기 빈번, 정합 중요 |
| 분석(Analytics) | 시세 통계 집계 제공 | 읽기 빈번, 저지연 요구 |
| 플랫폼(Platform) | 디스커버리·게이트웨이·설정 | 인프라 공통 |

> 경계 기준은 "변경 이유가 같은 것끼리 묶는다"입니다. 수집은 외부 API 스펙이 바뀌면, 분석은 통계 요건이 바뀌면 변합니다. 변경 축이 다르므로 분리합니다.

## 2. 모듈 분해 (Gradle 멀티모듈 MSA)

```
api-gateway ──→ (Eureka 디스커버리) ──→ ingestion / transaction / analytics
                                            │
config-server ── 설정·인증키 외부화          common(공유 계약) ← 세 도메인이 의존
```

| 모듈 | 유형 | 핵심 책임 |
| --- | --- | --- |
| service-discovery | 인프라 | Eureka 등록·발견 |
| config-server | 인프라 | 인증키·엔드포인트·회복력 정책 외부화 |
| api-gateway | 인프라 | 단일 진입점·라우팅 |
| common | 공유 라이브러리 | 표준 DTO·거래금액 파서(정합 규칙 1곳) |
| ingestion-service | 도메인 | 수집·정규화·회복력 (AC-1·2·3) |
| transaction-service | 도메인 | 멱등 적재·원본 조회 (AC-4) |
| analytics-service | 도메인 | 시세 통계 read model (AC-5) |

## 3. 런타임 토폴로지

```
[Client]
   │ POST /api/v1/ingest/apt-trade?lawdCd=&dealYmd=
   ▼
[api-gateway] ──lb──→ [ingestion-service] ──HTTP──→ data.go.kr (재시도·서킷)
                              │ 정규화(AC-3)
                              ▼ POST /transactions/bulk (멱등)
                       [transaction-service] (H2 / write model)
   │ GET /api/v1/market-stats?sggCd=&dealYear=&dealMonth=
   ▼
[api-gateway] ──lb──→ [analytics-service] ──lb──→ [transaction-service] 조회
                              │ 해제 제외·중위 집계(AC-3·5)
                              ▼ MarketStat (read model)
```

## 4. 사람이 판단한 지점 (Architectural Judgment): 이 강의의 핵심

아키텍처는 요구사항에서 기계적으로 도출되지 않습니다. **서비스 특성을 보고 사람이 트레이드오프를 판단해 결정**합니다. 이 프로젝트에서 사람이 내린 판단과 기각한 대안을 남깁니다.

### 판단 1. 수집과 조회를 분리할 것인가 (CQRS)
- **결정:** 분리한다. transaction은 write model, analytics는 read model.
- **근거:** 수집은 매월 배치성 쓰기, 조회는 상시 저지연 읽기로 부하 패턴이 정반대입니다. 같은 모델에 묶으면 배치 수집이 조회 지연을 유발합니다.
- **기각한 대안:** 단일 서비스 + DB 인덱스 튜닝. 초기에는 단순하지만, 통계 질의가 다양해지면 쓰기 모델을 오염시킵니다.
- **사람의 몫:** "이 서비스는 읽기·쓰기 부하가 다른가?"를 데이터로 판단해야 합니다. 다르지 않다면 CQRS는 과설계입니다.

### 판단 2. 수집을 별도 서비스로 뺄 것인가
- **결정:** 뺀다.
- **근거:** 외부 API(data.go.kr) 장애·트래픽 제한이 거래원장 쓰기에 전파되면 안 됩니다. 회복력 정책을 수집 경계에 가둡니다.
- **기각한 대안:** 거래원장이 직접 외부 호출. 장애 격리가 깨집니다.

### 판단 3. 정합 규칙(금액 파싱·해제 제외)을 어디 둘 것인가
- **결정:** common 공유 라이브러리에 둔다.
- **근거:** 같은 규칙을 수집·분석이 다르게 구현하면 통계가 어긋납니다. 한 곳에서 강제합니다.
- **사람의 몫:** 공유 라이브러리는 결합을 만듭니다. "정말 한 규칙인가"를 확인하고 공유합니다.

### 판단 4. 동기 호출인가 이벤트인가
- **결정(데모):** 동기 HTTP(WebClient + lb). 운영 확장 시 적재 이벤트 발행 → 분석 read model 사전 갱신으로 전환.
- **근거:** 데모는 흐름의 가시성이 우선입니다. 대규모 운영은 비동기가 맞지만, 처음부터 카프카를 넣으면 데모가 흐려집니다.
- **사람의 몫:** "지금 필요한 복잡도인가, 나중 복잡도인가"를 구분합니다.

> 정리: 위 네 판단 중 어느 것도 "정답"이 하나로 정해져 있지 않습니다. 청중에게 같은 요구사항으로 다른 경계도 가능함을 보이고, 왜 이 서비스에는 이 경계가 맞는지 토론으로 확정하십시오. SDD는 그 판단을 03_architecture에 근거와 함께 박제해, 이후 구현이 흔들리지 않게 합니다.

## 5. 다른 평면 명세 연결
- 데이터 모델: `04_data/realprice_data.md`
- API 계약: `05_api/realprice_api.md`
- 외부 연계 계약: `07_integration/molit_integration.md`

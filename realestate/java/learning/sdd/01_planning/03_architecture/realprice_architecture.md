# Architecture: RealField MSA 경계 설계 (realprice_architecture)

> SDD 1단계(01_planning) 정본. `01_feature/realprice_ingest.md`(AC-1~AC-5)와
> `00_sources/02_requirements/realfield-부동산실거래.md`의 서비스 특성을 근거로 MSA 경계를 정한다.
> 각 경계 결정은 근거와 기각한 대안을 함께 남긴다. 구조 규칙은
> `sdd/99_toolchain/01_automation/run_arch_check.py`가 기계로 강제하며, 본 문서가 그 규칙의 설계 근거다.

---

## 1. 이 서비스의 특성 (경계 설계 입력)

경계를 정하기 전에 실제로 다른 성격의 워크로드가 섞여 있는지부터 확인한다.

| 특성 축 | 관측 |
| --- | --- |
| 실패 도메인 | 외부 API(data.go.kr)는 지연·5xx·트래픽 초과(일 10,000건)로 실패한다(SIR-005, CONR-001). 이 실패가 거래 조회·시세 조회 가용성(PER-005)을 끌어내리면 안 된다. |
| 읽기/쓰기 비대칭 | 적재는 upsert 위주(자연키 충돌 처리, DAR-003)이고, 조회는 집계·중위값 연산 위주(DAR-007)다. 같은 인덱스·같은 트랜잭션 격리 수준으로 최적화할 수 없다(PER-001 vs PER-002). |
| 변경 빈도 | 수집 로직(XML 파싱, 회복력 정책)은 외부 API 변경에 따라 바뀌고, 원장 스키마(자연키)는 데이터 정합 요건에 따라 바뀌며, 통계 산식(중위값 정의)은 분석 요건에 따라 바뀐다. 세 축의 변경 트리거가 다르다. |
| 규모 | 전국 250개 시군구 × 월, 누적 수억 건(요구사항정의서 §2.3). 원장 적재량과 통계 조회 QPS가 함께 커지므로 write/read를 독립적으로 스케일해야 한다. |
| 규제·비식별 | 개인정보를 포함하지 않는 공개 데이터(SECR-004)이므로 컨텍스트 간 데이터 격리 요건은 낮다. 경계를 결정하는 힘은 프라이버시가 아니라 실패격리·읽기쓰기비대칭이다. |

이 다섯 축이 "왜 하나의 서비스가 아닌가"의 근거다. 아래 §2에서 이 축들을 각 경계 결정에 명시적으로 연결한다.

## 2. 경계 결정 (Decision Records)

### D-1. 수집(ingestion)과 거래원장(transaction)을 분리한다

- **결정**: 외부 API 수집·정규화는 `ingestion-service`, 거래원장 적재·조회(write model)는 `transaction-service`로 나눈다. ingestion은 정규화된 거래를 transaction의 적재 API로 전달한다.
- **근거**:
  - 실패 도메인이 다르다. 외부 API 실패(재시도·서킷오픈)가 거래원장의 upsert 트랜잭션이나 거래 조회(SFR-007) 가용성에 전파되면 안 된다(AC-2, PER-005).
  - 회복력 정책(resilience4j retry/circuit)은 ingestion에만 필요하다. transaction까지 이 정책을 공유하면 원장 쓰기 경로에 불필요한 복잡도가 들어간다.
  - 독립 배포·백필: 과거 구간 재수집(SFR-013)은 ingestion만 재실행하면 되고 transaction의 스키마·API는 영향받지 않는다.
- **기각한 대안**:
  - **단일 서비스로 통합(수집+원장)**: 수집 로직 변경(XML 필드 추가 등)이 원장 배포와 묶여 배포 위험이 커진다. 또 재시도 폭주 시 원장 쓰기 스레드풀까지 잠식할 위험이 있어 기각.
  - **수집을 배치 잡(별도 프로세스, 서비스 아님)으로만 두고 transaction에 직접 JDBC 적재**: 서비스 디스커버리·게이트웨이 노출이 안 되어 SFR-010(수동 트리거)의 API화가 어렵고, MSA 구조 게이트(공유 계약 의존 규칙)로 통일 검증이 안 됨. 기각.

### D-2. 거래원장(write model)과 시세 통계(read model)를 CQRS로 분리한다

- **결정**: `transaction-service`는 표준 거래 write model, `analytics-service`는 시세 통계 read model(MarketStat)로 분리한다. analytics는 transaction의 조회 API를 소스로 통계를 산출한다(SFR-009).
- **근거**:
  - 읽기/쓰기 비대칭(§1)이 명확하다. 원장은 자연키 upsert 최적화(단건 처리), 통계는 중위값 집계 최적화(범위 스캔)로 인덱스·쿼리 패턴이 근본적으로 다르다.
  - PER-003(조회·수집 부하 격리)이 요구사항으로 명시되어 있다. 수집 배치가 원장에 쓰기 부하를 걸어도 시세 통계 조회(PER-001, P99 300ms)는 별도 read model이라 영향받지 않는다.
  - 통계 산식(중위값 정의, 해제거래 제외 로직)이 바뀌어도 원장 스키마·적재 로직은 건드리지 않는다.
- **기각한 대안**:
  - **transaction-service 안에서 조회 시점에 집계 쿼리 실행(CQRS 없이 뷰/집계 쿼리만 추가)**: 구현은 간단하지만 PER-003을 구조적으로 보장할 수 없다. 원장 쓰기 트래픽이 늘면 집계 쿼리 성능이 함께 열화된다. 학습 목표(CQRS 분리 자체를 SFR-009로 명시)와도 배치되어 기각.
  - **analytics가 transaction의 DB를 직접 조회(DB 공유)**: 스키마 변경 시 두 서비스가 동시에 깨지는 강결합이 생기고, MSA 서비스 경계를 DB 레벨에서 무력화한다. 서비스 자율성 원칙 위반으로 기각.

### D-3. analytics는 이벤트/메시지 브로커가 아니라 동기 REST(`lb://transaction-service`)로 원장을 조회한다

- **결정**: 현재 단계에서 analytics-service는 Eureka 로드밸런싱 기반 REST 호출로 transaction-service를 동기 조회해 통계를 산출한다(`analytics-service/application.yml`의 `transaction.base-url=lb://transaction-service`가 현재 baseline).
- **근거**:
  - CONR-007(신규 외부 라이브러리·CLI 도입 최소화, 회복력은 resilience4j로 한정)이 메시지 브로커(Kafka 등) 신규 도입을 제약한다.
  - 현재 규모(학습 프로젝트 스캐폴드, 프로덕션 트래픽 없음)에서 이벤트 기반 아키텍처의 운영 복잡도(브로커 가용성, 컨슈머 오프셋 관리)를 정당화할 근거가 없다.
  - CQRS 분리(D-2)의 핵심 목표인 "조회 부하 격리"는 read model이 별도 서비스·별도 산출 경로를 갖는 것으로 이미 달성된다. 전달 메커니즘이 동기냐 비동기냐는 부차적이다.
- **기각한 대안**:
  - **이벤트 소싱/CDC(Kafka, Debezium 등)로 transaction 변경을 analytics에 스트리밍**: 정합성(적재 직후 통계 반영 지연 없음)과 결합도 측면에서 더 우수하지만, CONR-007 위반이고 현재 규모에 과도한 인프라(broker 클러스터 운영)다. 규모가 커지고 실시간성 요구가 명시되면 재검토 대상으로 `05_operate`에 후속 과제로 남긴다.
  - **analytics가 자체 배치로 원천(data.go.kr)을 다시 수집**: 정규화 로직(DAR-002 금액 변환, DAR-004 해제 판정)이 ingestion과 analytics 두 곳에 중복되어 정합 편차가 재발한다(요구사항정의서 §1.2 목적 3과 정면 배치). 기각.

### D-4. 공유 계약(자연키, 금액 파서, DTO)은 별도 서비스가 아니라 컴파일타임 라이브러리(`common`)로 둔다

- **결정**: `common` 모듈은 부트 실행 대상이 아닌 `java-library`로, AptTransaction 계약·자연키 규칙·금액 정규화 유틸을 도메인 모듈(ingestion/transaction/analytics)이 컴파일타임에 의존해 공유한다. common은 도메인 모듈에 역의존하지 않는다(구조 게이트 규칙 2).
- **근거**:
  - DAR-002(금액 정규화)·DAR-003(자연키)는 "여러 서비스가 각자 구현하면 정합이 어긋나는" 규칙이다. 요구사항정의서 §1.2 목적 3이 "수요자별 집계 편차 제거"를 명시한다. 런타임 호출보다 컴파일타임 공유 라이브러리가 이 불변 규칙을 더 강하게 강제한다(빌드 실패로 드리프트를 막음).
  - 자연키·금액 규칙은 변경 빈도가 낮고(데이터 계약 성격), 네트워크 홉을 둘 만큼 무거운 연산이 아니다.
- **기각한 대안**:
  - **"reference-data-service"로 자연키·금액 규칙을 API 노출**: 매 적재·집계 호출마다 네트워크 홉이 추가되고, 서비스 하나가 죽으면 모든 도메인 서비스의 적재·집계가 멈추는 단일 실패점이 생긴다. 규칙 자체가 순수 함수(문자열→값 변환)라 원격 호출을 정당화할 상태(state)가 없어 기각.
  - **각 서비스가 자체 구현**: 요구사항정의서 §1.2가 명시적으로 배제하는 상황(수요자별 집계 편차)을 재현하므로 기각.

### D-5. 플랫폼 공통(디스커버리·설정·게이트웨이)은 하나의 "platform-service"로 합치지 않고 개별 인프라 서비스로 유지한다

- **결정**: `service-discovery`(Eureka), `config-server`, `api-gateway`를 각각 독립 서비스로 유지한다. 셋을 묶어 도메인 경계(T4 플랫폼)로는 함께 다루되, 배포 단위는 나눈다.
- **근거**:
  - 부트스트랩 순서 의존성이 다르다: discovery가 먼저 뜨고(등록 대상), config-server가 그 다음(설정 공급자), gateway/도메인 서비스는 둘 다 필요(`99_toolchain/02_policies/deployment_order.md`). 이 순서 자체가 세 컴포넌트의 역할이 다름을 보여준다.
  - Spring Cloud 표준 컴포넌트(Eureka Server, Config Server, Gateway)는 각각 독립 배포·독립 장애 도메인으로 쓰도록 설계되어 있다. 합치면 Spring Cloud 관례를 벗어나 유지보수 비용만 늘어난다.
- **기각한 대안**:
  - **단일 platform-service로 통합**: 설정 서버가 죽으면 게이트웨이 라우팅까지 같이 죽는 결합이 생겨, 오히려 SIR-003(게이트웨이 단일 진입점) 가용성이 discovery/config 문제에 종속된다. 기각.

### D-6. 도메인 범위는 아파트 매매로 한정하고, 부동산 유형별·거래유형별 서비스 분화는 지금 하지 않는다

- **결정**: `ingestion-service`/`transaction-service`/`analytics-service`는 "아파트 매매 실거래"만 다룬다. 연립·다세대·오피스텔·단독/다가구, 전월세는 서비스 경계 후보에 넣지 않는다.
- **근거**: 요구사항정의서 §2.2가 명시적으로 제외 범위(확장 후보)로 못박았다. 아직 존재하지 않는 요구를 위해 경계를 미리 나누면 YAGNI 위반이고, 확장 시점에 실제 데이터 특성(원천 API 스펙 차이)을 보고 다시 나누는 편이 안전하다.
- **기각한 대안**:
  - **`property-type` 파라미터로 하나의 ingestion-service가 다중 유형을 수집**: 원천 API가 유형별로 엔드포인트·필드가 다르므로(예: 전월세는 보증금/월세 필드 추가) 조건 분기가 늘어나 SFR-003(표준 스키마 정규화) 로직이 유형마다 오염된다. 확장 시점에 유형별 ingestion 모듈을 추가하는 편이 낫다고 보고 기각(지금은 결정을 유보).

## 3. 서비스 경계 요약 (Context Map)

```text
                         ┌─────────────────────┐
                         │   api-gateway (8080) │  SIR-003 단일 진입점
                         └──────────┬───────────┘
              /api/v1/ingest/**     │     /api/v1/transactions/**   /api/v1/market-stats/**
        ┌────────────────┼─────────────────────┼────────────────────────────┐
        │                │                                                  │
┌───────▼────────┐  upsert 요청  ┌───────▼─────────────┐   REST 조회(lb://) ┌───▼──────────────┐
│ ingestion-service│ ───────────▶ │ transaction-service  │ ◀───────────────── │ analytics-service │
│   T1 (8081)     │  D-1         │   T2 (8082, write)   │  D-2/D-3           │   T3 (8083, read) │
│ data.go.kr 수집  │              │ 자연키 upsert 원장   │                    │ MarketStat 집계    │
└───────┬─────────┘              └──────────┬───────────┘                    └────────┬───────────┘
        │                                    │                                          │
        └───────────────┬────────────────────┴──────────────────────────────────────────┘
                         │ compile-time 의존 (D-4)
                 ┌───────▼────────┐
                 │     common      │  자연키·금액 파서·DTO (java-library, 도메인 역의존 금지)
                 └─────────────────┘

플랫폼(T4, D-5): service-discovery(8761, Eureka) · config-server(8888) · api-gateway(8080)
  - 모든 도메인 서비스가 Eureka에 등록되고, config-server에서 설정을 받는다(수집 서비스는 molit.*).
```

## 4. 경계별 책임·소유 (Ownership)

| 경계 | 서비스 | 핵심 책임 | 관련 AC | 소유 에이전트 |
| --- | --- | --- | --- | --- |
| T1 수집 | `ingestion-service` | data.go.kr 호출·페이징·XML 파싱·회복력·정규화 | AC-1, AC-2, AC-3(금액/해제 변환), AC-4(재수집) | `ingestion-dev` |
| T2 거래원장 | `transaction-service` | 표준 거래 write model, 자연키 upsert, 거래 조회 | AC-1, AC-3(canceled 보존), AC-4, AC-5(원장 조회) | `transaction-dev` |
| T3 분석 | `analytics-service` | MarketStat read model, 중위값 집계, 해제거래 제외 | AC-3(집계 제외), AC-5 | `analytics-dev` |
| T4 플랫폼 | `service-discovery`, `config-server`, `api-gateway` | 디스커버리, 설정 외부화, 단일 진입점 라우팅 | AC-1(SIR-003/004), AC-2(회복력 설정 공급) | `platform-dev` |
| 공유 계약 | `common` | AptTransaction 계약, 자연키 규칙, 금액 정규화 유틸 | AC-3, AC-4 | `backend-dev`(경계 간 계약), 각 도메인 에이전트가 소비 |

## 5. 구조 게이트 정합성

본 문서의 결정은 `sdd/99_toolchain/01_automation/run_arch_check.py`가 강제하는 5개 규칙과 1:1로 대응한다.

| 게이트 규칙 | 대응 결정 |
| --- | --- |
| 필수 7개 모듈 포함 | D-1, D-2, D-5 (T1/T2/T3 분리 + 플랫폼 3종 개별 유지) |
| common이 도메인에 역의존하지 않음 | D-4 |
| 각 도메인이 common에 의존 | D-4 |
| 게이트웨이 3개 라우트 단일 진입점 | D-5, §3 다이어그램의 `/api/v1/*` 라우팅 |
| analytics가 transaction을 조회(CQRS) | D-2, D-3 |

## 6. 후속 재검토 트리거

- analytics 통계 반영 지연이 실측으로 문제가 되면 D-3(REST 동기 조회)을 이벤트 기반으로 재검토한다.
- 아파트 외 유형·전월세로 범위가 확장되면 D-6을 재검토하고 신규 ingestion 모듈 분리 여부를 판단한다.
- 규모가 커져 config-server/service-discovery 자체가 병목이 되면 D-5의 개별 배포 단위를 유지한 채 다중 인스턴스·클러스터링을 검토한다(경계 자체는 유지).

# Nonfunctional: RealField 실거래 수집·조회 비기능 요구 (realprice_nonfunctional)

> SDD 1단계(01_planning) 정본. `00_sources/02_requirements/realfield-부동산실거래.md`의
> 성능요구사항(PER)·제약사항(CONR) 일부·인터페이스 회복력(SIR-005)을 검증 가능한 비기능 수용기준으로 정제한다.
> 기능 수용기준(AC-1~AC-5)은 `01_planning/01_feature/realprice_ingest.md`가 정본이며, 본 문서는 그 성능·
> 신뢰성·확장성·운영 제약 축을 다룬다.

---

## 1. 성능 (Performance)

| ID | 항목 | 목표 | 측정 조건 | 검증 |
| --- | --- | --- | --- | --- |
| NFR-PERF-001 | 시세 통계 조회 응답시간 | P99 300ms 이내 | 단일 시군구·계약월 조건, analytics-service read model 직접 조회 | 시험(부하테스트) |
| NFR-PERF-002 | 수집 처리량 | 시군구당 1만 건/분 이상 수집·정규화 | `numOfRows`를 최대 1000으로 설정해 페이징 호출 수 최소화 | 시험 |
| NFR-PERF-003 | 조회·수집 부하 격리 | 수집 배치 실행 중에도 NFR-PERF-001 열화 없음 | CQRS로 write model(transaction-service)과 read model(analytics-service)을 분리 실행 | 분석 + 부하테스트 동시 실행 |

- 근거: PER-001, PER-002, PER-003. AC-2·AC-5(`01_feature/realprice_ingest.md`)와 정합한다.
- NFR-PERF-003 검증은 수집 배치를 강제 구동한 상태에서 NFR-PERF-001의 부하테스트를 동시에 수행해
  두 지표가 서로 간섭하지 않음을 확인한다.

## 2. 신뢰성·회복력 (Reliability / Resilience)

| ID | 항목 | 목표 | 근거 |
| --- | --- | --- | --- |
| NFR-REL-001 | 외부 API 재시도 | resilience4j retry, `max-attempts=3`, `wait-duration=500ms` | SIR-005, `config-server/config/ingestion-service.yml` 현재 값 |
| NFR-REL-002 | 서킷브레이커 | `sliding-window-size=20`, `failure-rate-threshold=50%`, `wait-duration-in-open-state=10s` | SIR-005 |
| NFR-REL-003 | 부분 수집 허용 | 일부 시군구·페이지 실패 시에도 배치 전체를 중단하지 않고 성공 구간은 적재 | SFR-011 |
| NFR-REL-004 | 트래픽 한도 준수 | 개발계정 일일 10,000건 한도 내에서 동작(백오프/이월) | CONR-001, SIR-005 |
| NFR-REL-005 | 핵심 조회 가용성 | 핵심 조회 경로(거래 조회·시세 통계 조회) 99.9% 가용성. 무중단 배포·롤백 지원 | PER-005 |

- 회복력 정책 값(재시도 횟수, 서킷 임계치, 백오프 전략)의 확정 정본은 `01_planning/07_integration`
  (후속 작성 대상)로 승격하며, 본 문서는 현재 config-server 값을 참고 baseline으로만 기록한다.

## 3. 확장성 (Scalability)

| ID | 항목 | 목표 | 근거 |
| --- | --- | --- | --- |
| NFR-SCALE-001 | 대상 규모 | 전국 250개 시군구 × 월 단위, 누적 수억 건 | 요구사항정의서 §2.3 |
| NFR-SCALE-002 | 동시 수집 제어 | 다중 시군구 동시 수집 시에도 일일 트래픽 한도(10,000건)를 초과하지 않도록 호출을 조절 | PER-004 |
| NFR-SCALE-003 | 페이징 효율 | `numOfRows` 최대치(1000) 사용으로 호출 수 최소화 | PER-002 |

## 4. 운영 제약 (Operational Constraints)

| ID | 항목 | 내용 | 근거 |
| --- | --- | --- | --- |
| NFR-OPS-001 | 스택 고정 | Java 21 / Spring Boot 3.5.x / Spring Cloud 2025.0(Northfields) / Gradle 멀티모듈 | CONR-006 |
| NFR-OPS-002 | 신규 의존성 최소화 | 회복력 라이브러리는 resilience4j로 한정, 신규 외부 라이브러리·CLI 도입 최소화 | CONR-007 |
| NFR-OPS-003 | 원천 응답 형 변환 책임 | 외부 응답은 전량 XML 문자열이며, 숫자·날짜 형 변환은 시스템 책임 | CONR-002 |
| NFR-OPS-004 | 배포 순서 | main push → DEV 배포 → DEV 검증 순서를 따른다 | `.claude/CLAUDE.md`, `99_toolchain/02_policies/deployment_order.md` |

## 5. 요구사항 추적표

| NFR 그룹 | 관련 PER/SIR/CONR | 관련 AC |
| --- | --- | --- |
| 성능(§1) | PER-001, PER-002, PER-003 | AC-2, AC-5 |
| 신뢰성(§2) | SIR-005, SFR-011, CONR-001, PER-005 | AC-2 |
| 확장성(§3) | PER-002, PER-004 | AC-1, AC-2 |
| 운영 제약(§4) | CONR-002, CONR-006, CONR-007 | AC-1, AC-3 |

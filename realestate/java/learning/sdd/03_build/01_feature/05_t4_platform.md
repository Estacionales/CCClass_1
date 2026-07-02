# T4 · 플랫폼(service-discovery·config-server·api-gateway) · 구현 요약 (03_build)

> SDD 'build' 산출물. current-state only — dated execution narrative 금지.
> 대상 위치: `sdd/03_build/01_feature/05_t4_platform.md`
> 소유 에이전트: `platform-dev`. 건드린 모듈: 인프라 3종(`service-discovery`, `config-server`,
> `api-gateway`)만. 도메인 코드(`common`·T1/T2/T3)는 미터치.

## 구현 범위
- 구현한 기능/경계:
  - 인프라 3종의 부트스트랩 진입 클래스 신규 작성(각 모듈에 메인 소스가 전혀 없던 상태에서 복원).
    레퍼런스 솔루션(`solution/<module>/kr/elice/realfield/**`)과 패키지·클래스명·애너테이션·main 시그니처
    1:1 동일. 각 ~12줄의 최소 부트스트랩(추가 빈·설정 없음).
  - `service-discovery`: Eureka 서버 활성화(`@EnableEurekaServer` + `@SpringBootApplication`).
    도메인 서비스가 등록·발견되는 단일 레지스트리(SIR-004의 등록 기반).
  - `config-server`: 설정 서버 활성화(`@EnableConfigServer` + `@SpringBootApplication`).
    data.go.kr 인증키·엔드포인트·회복력 정책을 외부화해 각 서비스가 기동 시 받아간다(SECR-001/002).
  - `api-gateway`: 단일 진입점 활성화(plain `@SpringBootApplication`). 라우팅은 전적으로 설정 주도라
    별도 enabling 애너테이션이 없다 — 라우트 정의는 `application.yml`이 정본(SIR-003).
  - config-server 외부화 설정의 엔드포인트 드리프트 1건 정정(아래 참조).

## 변경 모듈
- service-discovery:
  - `kr.elice.realfield.discovery.DiscoveryApplication` — 신규. `@EnableEurekaServer`
    `@SpringBootApplication` + `main`.
  - `src/main/resources/application.yml` — 미변경. 포트 8761, `register-with-eureka: false` /
    `fetch-registry: false`(서버 자신은 등록하지 않음), self-preservation on.
  - `build.gradle` — 미변경(`spring-cloud-starter-netflix-eureka-server` 이미 선언됨).
- config-server:
  - `kr.elice.realfield.config.ConfigServerApplication` — 신규. `@EnableConfigServer`
    `@SpringBootApplication` + `main`.
  - `src/main/resources/config/ingestion-service.yml` — `molit.apt-trade-path`를 기본(비-Dev)
    `/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade` → 상세(Dev)
    `/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev`로 정정(1값). 근거·정본은
    `01_planning/07_integration/molit_integration.md` §1. 이 값 하나만 변경(다른 키·resilience4j 정책값
    미변경).
  - `src/main/resources/application.yml` — 미변경. 포트 8888, native profile, `search-locations:
    classpath:/config`.
  - `build.gradle` — 미변경(`spring-cloud-config-server` 이미 선언됨).
- api-gateway:
  - `kr.elice.realfield.gateway.ApiGatewayApplication` — 신규. plain `@SpringBootApplication` + `main`.
    (라우팅이 설정 주도이므로 게이트웨이용 enabling 애너테이션 없음 — 의도된 최소 형태.)
  - `src/main/resources/application.yml` — 미변경. 포트 8080 단일 진입점, discovery locator on,
    명시 라우트 3종(아래 §계약·자산).
  - `build.gradle` — 미변경(`spring-cloud-starter-gateway` + `spring-cloud-starter-netflix-eureka-client`
    이미 선언됨).

## 계약·자산
- 라우팅 계약(SIR-003, `api-gateway/application.yml` 정본 — 본 턴 미변경, 유지·검증만):
  - `/api/v1/ingest/**` → `lb://ingestion-service`
  - `/api/v1/transactions/**` → `lb://transaction-service`
  - `/api/v1/market-stats/**` → `lb://analytics-service`
  - 세 라우트 모두 Eureka 등록 서비스명 기반 `lb://` 로드밸런싱. discovery locator(`lower-case-service-id`)
    도 켜져 있어 등록 서비스명 자동 라우팅이 보조된다.
  - 서비스 간 전용 경로 `POST /internal/transactions/batch-upsert`(`05_api` §3b)는 게이트웨이 라우트에
    **미노출**(외부 노출 금지 확인). CQRS read 분리(analytics → `lb://transaction-service` 조회)는
    analytics-service(T3) 내부 계약이며 게이트웨이 외부 경로로 노출되지 않는다.
- 설정 외부화 계약(SECR-001/002, config-server가 배포):
  - 인증키는 `service-key: ${MOLIT_SERVICE_KEY:}` 환경변수 참조만 — 파일·이미지·로그에 평문 비밀값 없음.
  - MOLIT 엔드포인트(`base-url` + `apt-trade-path`)·`num-of-rows`·resilience4j(circuitbreaker/retry)
    정책값을 `ingestion-service.yml`로 외부화. resilience4j 정책값 정본은
    `07_integration/molit_integration.md` §4이며 현재 파일 값과 동일.
  - 엔드포인트 값 정합: config-server 복사본(T4 소유)과 T1 소유 `ingestion-service/application.yml`
    로컬 복사본이 상세(Dev) 엔드포인트로 최종 일치(`02_t1_ingestion.md` §드리프트 정정).
- 기동/배포 순서(정책 정본 `99_toolchain/02_policies/deployment_order.md`):
  discovery(8761) → config-server(8888) → api-gateway(8080) → 도메인 서비스(8081~8083).

## 현재 사용자 가시 동작
- 세 인프라 앱이 이제 부팅 가능한 진입 클래스를 갖는다: Eureka 콘솔(8761), Config 서버(8888),
  단일 진입 게이트웨이(8080). 부트스트랩 복원 전에는 메인 소스 부재로 기동 자체가 불가능했다.
- 외부 클라이언트 관점의 end-to-end 라우팅은 대상 도메인 서비스가 Eureka에 등록되어야 성립한다.
  본 저장소는 세 도메인 라우트를 모두 정의해 두었으나(설정 정본), 실제 라우팅 성공은 각 도메인 서비스
  (T1/T2/T3) 등록 여부에 달려 있다(런타임 확인은 §검증 참조).

## 본 턴에서 구현하지 않은 T4 항목(명시적 범위 밖)
- 헬스체크·actuator 엔드포인트, 게이트웨이 필터/CORS/타임아웃 등 부가 설정 — 요청 범위 밖.
- 배포 순서 자동화 기동 스크립트 — 정책 문서만 존재, 스크립트 미작성.
- config-server 운영용 git backend·설정값 암호화(현재 데모는 native profile classpath 설정).
- 도메인 서비스 내부 구현(T1/T2/T3 메인 소스)과 `common` — 병렬 트랙 소관, 미터치.
- service-discovery 실기동 후 도메인 3종 등록의 런타임 확인(T2/T3 완성·기동 후 오케스트레이션에서 수행).

## 검증한 회귀 범위
- 직접(인프라 3모듈): 부트스트랩 3종을 레퍼런스 솔루션과 1:1 대조(패키지·클래스명·애너테이션·main 동일).
  이들은 plain 부트스트랩이라 이를 고정하는 JUnit 핀 테스트가 없다 — 레퍼런스 솔루션이 정본.
- 구조 게이트: `python sdd/99_toolchain/01_automation/run_arch_check.py` → `RESULT: PASS (7/7)`.
  - 규칙 4(게이트웨이 3라우트 = ingest·transactions·market-stats)는 T4 책임이며 PASS.
    이 규칙은 `api-gateway/src/main/resources/application.yml`만 읽으므로 본 턴 yml 미변경으로 유지.
  - 나머지 규칙(필수 7모듈, common 역의존 없음, 도메인 3종 → common 의존, analytics → transaction
    CQRS read)의 PASS는 저장소 전체 현재 상태 관측치다. `02_t1_ingestion.md` 시점의 `5/7`에서
    T2/T3 → common 의존 2건이 PASS로 바뀐 것은 병렬 트랙이 두 도메인 서비스 메인 소스를 올린 결과이며
    T4 변경분이 아니다.
- 오케스트레이션 세션 독립 재검증(T2/T3/T4 병렬 트랙 완료 후): `./gradlew test` 전 모듈 BUILD
  SUCCESSFUL. `./gradlew :api-gateway:bootJar :config-server:bootJar :service-discovery:bootJar` →
  BUILD SUCCESSFUL — 세 인프라 모듈이 실제로 실행 가능한 부트 jar를 패키징한다(부트스트랩 클래스가
  없던 이전 상태에서는 `bootJar`가 `mainClass 미설정` 오류로 실패했었다). `run_arch_check.py` 7/7 PASS 재확인.
- 여전히 미실행: 다섯 서비스를 동시 기동해 discovery 콘솔(`http://localhost:8761`)에서 실제 등록을
  눈으로 확인하는 라이브 런타임 검증. T2/T3에 `@SpringBootApplication` 부트스트랩이 아직 없어
  (본 턴 의도된 범위 밖) 두 도메인 서비스는 애초에 기동 자체가 불가능하므로, 5서비스 동시 등록 확인은
  그 부트스트랩들이 추가되는 후속 턴으로 미룬다.
